import { useEffect, useState } from 'react';
import { Alert, Box, Button, Stack, Typography } from '@mui/material';
import { Link as RouterLink, useParams } from 'react-router-dom';
import {
  getCampaignBattleMaps,
  getCampaignMonsters,
  getCampaignScenes,
  getCampaignState,
  getCharacterInventory,
  getMonsters,
} from '../api/campaigns';
import { connectCampaignWebSocket, type CampaignWebSocketEvent } from '../api/websocket';
import { BattleMapPanel } from '../components/campaign/BattleMapPanel';
import { CampaignHeader } from '../components/campaign/CampaignHeader';
import { CharacterList } from '../components/campaign/CharacterList';
import { DmControls } from '../components/campaign/DmControls';
import { EventList } from '../components/campaign/EventList';
import { InventoryPanel } from '../components/campaign/InventoryPanel';
import { MonsterList } from '../components/campaign/MonsterList';
import { ScenePanel } from '../components/campaign/ScenePanel';
import { PageShell } from '../components/PageShell';
import { useAuth } from '../hooks/useAuth';
import { getApiErrorMessage } from '../lib/apiError';
import type {
  CampaignBattleMapDetails,
  CampaignEventState,
  CampaignSceneState,
  CampaignState,
} from '../types/campaignState';
import type { MonsterSummary } from '../types/monster';
import type { CharacterInventoryItem } from '../types/inventory';

type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'reconnecting';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function getNumberValue(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function getStringValue(value: unknown): string | null {
  return typeof value === 'string' ? value : null;
}

function buildLocalEvent(
  campaignId: number,
  type: string,
  data: Record<string, unknown>
): CampaignEventState {
  return {
    id: Date.now() + Math.floor(Math.random() * 1000),
    campaign_id: campaignId,
    type,
    data,
    created_at: new Date().toISOString(),
  };
}

function toCampaignScene(
  campaignId: number,
  payload: Record<string, unknown>,
  fallbackCreatedAt: string
): CampaignSceneState | null {
  const sceneId = getNumberValue(payload.scene_id ?? payload.id);

  if (sceneId === null) {
    return null;
  }

  return {
    id: sceneId,
    campaign_id: campaignId,
    title: getStringValue(payload.title) ?? 'Сцена',
    description: getStringValue(payload.description) ?? '',
    image_url: payload.image_url == null ? null : getStringValue(payload.image_url),
    is_active: Boolean(payload.is_active),
    created_at: getStringValue(payload.created_at) ?? fallbackCreatedAt,
  };
}

function updateCampaignMonsters(
  currentState: CampaignState | null,
  monsters: CampaignState['monsters']
): CampaignState | null {
  if (!currentState) {
    return currentState;
  }

  return {
    ...currentState,
    monsters,
  };
}

function updateCharacterHp(
  currentState: CampaignState | null,
  characterId: number,
  hp: number
): CampaignState | null {
  if (!currentState) {
    return currentState;
  }

  return {
    ...currentState,
    characters: currentState.characters.map((character) =>
      character.id === characterId ? { ...character, current_hp: hp } : character
    ),
  };
}

function updateTokenPosition(
  currentState: CampaignState | null,
  tokenId: number,
  x: number,
  y: number
): CampaignState | null {
  if (!currentState) {
    return currentState;
  }

  return {
    ...currentState,
    battle_maps: currentState.battle_maps.map((battleMap) => ({
      ...battleMap,
      tokens: battleMap.tokens.map((token) => (token.id === tokenId ? { ...token, x, y } : token)),
    })),
  };
}

function appendEvent(currentState: CampaignState | null, event: CampaignEventState): CampaignState | null {
  if (!currentState) {
    return currentState;
  }

  return {
    ...currentState,
    recent_events: [...currentState.recent_events, event],
  };
}

export function CampaignPage() {
  const { campaignId } = useParams();
  const [campaignState, setCampaignState] = useState<CampaignState | null>(null);
  const [campaignScenes, setCampaignScenes] = useState<CampaignSceneState[]>([]);
  const [battleMapDetails, setBattleMapDetails] = useState<CampaignBattleMapDetails[]>([]);
  const [availableMonsters, setAvailableMonsters] = useState<MonsterSummary[]>([]);
  const [inventoriesByCharacterId, setInventoriesByCharacterId] = useState<Record<number, CharacterInventoryItem[]>>({});
  const [isLoading, setIsLoading] = useState(Boolean(campaignId));
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const { user, token } = useAuth();
  const [loadedCampaignId, setLoadedCampaignId] = useState<number | null>(null);
  const isDm = user?.role === 'dm';

  useEffect(() => {
    let isActive = true;

    async function loadCampaignData() {
      if (!campaignId) {
        if (isActive) {
          setCampaignState(null);
          setCampaignScenes([]);
          setBattleMapDetails([]);
          setAvailableMonsters([]);
          setInventoriesByCharacterId({});
          setLoadedCampaignId(null);
          setIsLoading(false);
          setError(null);
        }
        return;
      }

      const parsedCampaignId = Number(campaignId);

      if (Number.isNaN(parsedCampaignId)) {
        if (isActive) {
          setCampaignState(null);
          setCampaignScenes([]);
          setBattleMapDetails([]);
          setAvailableMonsters([]);
          setInventoriesByCharacterId({});
          setLoadedCampaignId(null);
          setIsLoading(false);
          setError('Некорректный идентификатор кампании.');
        }
        return;
      }

      if (isActive) {
        setIsLoading(true);
        setError(null);
      }

      try {
        const [stateResult, battleMapsResult, scenesResult, monstersResult] = await Promise.allSettled([
          getCampaignState(parsedCampaignId),
          getCampaignBattleMaps(parsedCampaignId),
          getCampaignScenes(parsedCampaignId),
          isDm ? getMonsters() : Promise.resolve({ data: [] as MonsterSummary[] }),
        ]);

        if (stateResult.status === 'rejected') {
          throw stateResult.reason;
        }

        if (!isActive) {
          return;
        }

        setCampaignState(stateResult.value.data);
        setLoadedCampaignId(parsedCampaignId);
        setBattleMapDetails(battleMapsResult.status === 'fulfilled' ? battleMapsResult.value.data : []);
        setCampaignScenes(scenesResult.status === 'fulfilled' ? scenesResult.value.data : []);
        setAvailableMonsters(monstersResult.status === 'fulfilled' ? monstersResult.value.data : []);

        const characterInventories = await Promise.allSettled(
          stateResult.value.data.characters.map((character) => getCharacterInventory(character.id))
        );

        if (!isActive) {
          return;
        }

        const nextInventories: Record<number, CharacterInventoryItem[]> = {};
        characterInventories.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            const character = stateResult.value.data.characters[index];
            nextInventories[character.id] = result.value.data;
          }
        });

        setInventoriesByCharacterId(nextInventories);
      } catch (requestError) {
        if (!isActive) {
          return;
        }

        setCampaignState(null);
        setCampaignScenes([]);
        setBattleMapDetails([]);
        setAvailableMonsters([]);
        setInventoriesByCharacterId({});
        setError(getApiErrorMessage(requestError, 'Не удалось загрузить state кампании.'));
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    void loadCampaignData();

    return () => {
      isActive = false;
    };
  }, [campaignId, isDm, reloadToken]);

  useEffect(() => {
    let isActive = true;

    if (!campaignId || !token) {
      setConnectionStatus('disconnected');
      return;
    }

    const parsedCampaignId = Number(campaignId);

    if (Number.isNaN(parsedCampaignId) || loadedCampaignId !== parsedCampaignId) {
      setConnectionStatus('disconnected');
      return;
    }

    setConnectionStatus('connecting');

    const connection = connectCampaignWebSocket({
      campaignId: parsedCampaignId,
      token,
      onOpen: () => {
        if (isActive) {
          setConnectionStatus('connected');
        }
      },
      onClose: (event) => {
        if (!isActive) {
          return;
        }

        if (event.code === 1000 || event.code === 1008) {
          setConnectionStatus('disconnected');
          return;
        }

        setConnectionStatus('reconnecting');
      },
      onError: () => {
        if (isActive) {
          setConnectionStatus('disconnected');
        }
      },
      onMessage: (message: CampaignWebSocketEvent) => {
        if (!isActive) {
          return;
        }

        const payload = isRecord(message.data) ? message.data : {};
        const fallbackCreatedAt = new Date().toISOString();

        if (message.type === 'monster_added') {
          const monsterId = getNumberValue(payload.monster_id);
          if (monsterId !== null) {
            void getCampaignMonsters(parsedCampaignId)
              .then((response) => {
                if (!isActive) {
                  return;
                }
                setCampaignState((currentState) => updateCampaignMonsters(currentState, response.data));
              })
              .catch(() => undefined);
            setCampaignState((currentState) => appendEvent(currentState, buildLocalEvent(parsedCampaignId, message.type, payload)));
          }
          return;
        }

        if (message.type === 'hp_updated') {
          const characterId = getNumberValue(payload.character_id);
          const hp = getNumberValue(payload.hp);

          if (characterId !== null && hp !== null) {
            setCampaignState((currentState) => updateCharacterHp(currentState, characterId, hp));
            setCampaignState((currentState) => appendEvent(currentState, buildLocalEvent(parsedCampaignId, message.type, payload)));
          }
          return;
        }

        if (message.type === 'inventory_updated') {
          const characterId = getNumberValue(payload.character_id);

          if (characterId !== null) {
            void getCharacterInventory(characterId)
              .then((response) => {
                if (!isActive) {
                  return;
                }
                setInventoriesByCharacterId((current) => ({
                  ...current,
                  [characterId]: response.data,
                }));
              })
              .catch(() => undefined);
            setCampaignState((currentState) => appendEvent(currentState, buildLocalEvent(parsedCampaignId, message.type, payload)));
          }
          return;
        }

        if (message.type === 'scene_changed') {
          const scene = toCampaignScene(parsedCampaignId, payload, fallbackCreatedAt);

          if (scene) {
            setCampaignState((currentState) =>
              currentState
                ? {
                    ...currentState,
                    current_scene: scene,
                  }
                : currentState
            );
            setCampaignScenes((currentScenes) => {
              const existingIndex = currentScenes.findIndex((entry) => entry.id === scene.id);

              if (existingIndex === -1) {
                return currentScenes.map((entry) => ({
                  ...entry,
                  is_active: entry.id === scene.id,
                })).concat(scene);
              }

              return currentScenes.map((entry) =>
                entry.id === scene.id
                  ? {
                      ...entry,
                      ...scene,
                    }
                  : {
                      ...entry,
                      is_active: entry.id === scene.id,
                    }
              );
            });
            setCampaignState((currentState) => appendEvent(currentState, buildLocalEvent(parsedCampaignId, message.type, payload)));
          }
          return;
        }

        if (message.type === 'token_moved') {
          const tokenId = getNumberValue(payload.token_id);
          const x = getNumberValue(payload.x);
          const y = getNumberValue(payload.y);

          if (tokenId !== null && x !== null && y !== null) {
            setCampaignState((currentState) => updateTokenPosition(currentState, tokenId, x, y));
            setCampaignState((currentState) => appendEvent(currentState, buildLocalEvent(parsedCampaignId, message.type, payload)));
          }
          return;
        }

        if (message.type === 'system') {
          setCampaignState((currentState) => appendEvent(currentState, buildLocalEvent(parsedCampaignId, message.type, payload)));
        }
      },
    });

    return () => {
      isActive = false;
      connection.close();
      setConnectionStatus('disconnected');
    };
  }, [campaignId, loadedCampaignId, token]);

  if (!campaignId) {
    return (
      <PageShell title="Campaign">
        <Stack spacing={1.5}>
          <Typography variant="h6">Выберите кампанию на Dashboard.</Typography>
          <Typography color="text.secondary">
            Здесь будет показано состояние кампании после перехода по ссылке Open.
          </Typography>
          <Box>
            <Button component={RouterLink} to="/dashboard" variant="contained">
              Go to Dashboard
            </Button>
          </Box>
        </Stack>
      </PageShell>
    );
  }

  const parsedCampaignId = Number(campaignId);
  const activeCampaign = campaignState?.campaign ?? null;
  const participantsCount = campaignState?.characters.length ?? 0;
  const battleMaps = campaignState?.battle_maps ?? [];
  const visibleEvents = campaignState ? [...campaignState.recent_events].reverse() : [];
  const battleMapDetailsById = new Map(battleMapDetails.map((battleMap) => [battleMap.id, battleMap]));
  const dmLabel = activeCampaign && user && activeCampaign.dm_id === user.id ? 'Вы' : activeCampaign ? `#${activeCampaign.dm_id}` : '—';
  const handleRefresh = () => setReloadToken((value) => value + 1);

  if (Number.isNaN(parsedCampaignId)) {
    return (
      <PageShell title="Campaign">
        <Alert severity="error">Некорректный идентификатор кампании.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell title="Campaign">
      <Stack spacing={2}>
        {error ? <Alert severity="error">{error}</Alert> : null}

        <CampaignHeader
          campaign={activeCampaign}
          campaignId={parsedCampaignId}
          participantCount={participantsCount}
          dmLabel={dmLabel}
          connectionStatus={connectionStatus}
          isLoading={isLoading}
          onRefresh={handleRefresh}
        />

        {isDm ? (
          <DmControls
            campaignId={parsedCampaignId}
            characters={campaignState?.characters ?? []}
            scenes={campaignScenes}
            availableMonsters={availableMonsters}
            battleMaps={battleMaps}
            battleMapDetailsById={battleMapDetailsById}
          />
        ) : null}

        <CharacterList characters={campaignState?.characters ?? []} isLoading={isLoading} />
        <InventoryPanel
          characters={campaignState?.characters ?? []}
          inventoriesByCharacterId={inventoriesByCharacterId}
          isLoading={isLoading}
        />
        <MonsterList monsters={campaignState?.monsters ?? []} isLoading={isLoading} />
        <ScenePanel currentScene={campaignState?.current_scene ?? null} scenes={campaignScenes} isLoading={isLoading} />
        <EventList events={visibleEvents} isLoading={isLoading} />
        <BattleMapPanel battleMaps={battleMaps} battleMapDetailsById={battleMapDetailsById} isLoading={isLoading} />
      </Stack>
    </PageShell>
  );
}
