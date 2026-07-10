import { useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Paper,
  Stack,
  Tooltip,
  Typography,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import { getCampaignBattleMaps, getCampaigns, getCampaignState, moveBattleToken } from '../api/campaigns';
import { connectCampaignWebSocket, type CampaignWebSocketEvent } from '../api/websocket';
import { useAuth } from '../hooks/useAuth';
import { getApiErrorMessage } from '../lib/apiError';
import type { Campaign } from '../types/campaign';
import type { CampaignBattleMapDetails, CampaignBattleMapState, CampaignState } from '../types/campaignState';

type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'reconnecting';

type TokenKind = 'character' | 'monster' | 'unknown';

type TokenViewModel = {
  id: number;
  name: string;
  kind: TokenKind;
  x: number;
  y: number;
  hpLabel: string | null;
  color: string;
};

type DragState = {
  tokenId: number;
  x: number;
  y: number;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function getNumberValue(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
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

function resolveBattleMapName(
  battleMap: CampaignBattleMapState,
  battleMapDetailsById: Map<number, CampaignBattleMapDetails>
) {
  return battleMapDetailsById.get(battleMap.id)?.name ?? `Боевая карта #${battleMap.id}`;
}

function resolveTokenViewModel(
  token: CampaignBattleMapState['tokens'][number],
  campaignState: CampaignState | null
): TokenViewModel {
  const character = campaignState?.characters.find((entry) => entry.id === token.character_id) ?? null;
  const monsterState =
    campaignState?.monsters.find((entry) => entry.monster.id === token.monster_id || entry.monster_id === token.monster_id) ??
    null;

  if (character) {
    return {
      id: token.id,
      name: character.name,
      kind: 'character',
      x: token.x,
      y: token.y,
      hpLabel: `${character.current_hp}/${character.max_hp}`,
      color: '#2563eb',
    };
  }

  if (monsterState) {
    return {
      id: token.id,
      name: monsterState.monster.name,
      kind: 'monster',
      x: token.x,
      y: token.y,
      hpLabel: `${monsterState.monster.hp}`,
      color: '#dc2626',
    };
  }

  return {
    id: token.id,
    name: `Token #${token.id}`,
    kind: 'unknown',
    x: token.x,
    y: token.y,
    hpLabel: null,
    color: '#64748b',
  };
}

export function BattlePage() {
  const { user, token } = useAuth();
  const isDm = user?.role === 'dm';
  const [searchParams, setSearchParams] = useSearchParams();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [campaignState, setCampaignState] = useState<CampaignState | null>(null);
  const [battleMapDetails, setBattleMapDetails] = useState<CampaignBattleMapDetails[]>([]);
  const [campaignsLoading, setCampaignsLoading] = useState(true);
  const [campaignLoading, setCampaignLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [selectedTokenId, setSelectedTokenId] = useState<number | null>(null);
  const [boardWidth, setBoardWidth] = useState(0);
  const [dragState, setDragState] = useState<DragState | null>(null);
  const [moveError, setMoveError] = useState<string | null>(null);
  const boardScrollRef = useRef<HTMLDivElement | null>(null);
  const dragStateRef = useRef<DragState | null>(null);

  const selectedCampaignId = useMemo(() => {
    const rawValue = searchParams.get('campaignId');
    if (!rawValue) {
      return null;
    }

    const parsed = Number(rawValue);
    return Number.isNaN(parsed) ? null : parsed;
  }, [searchParams]);

  const selectedMapId = useMemo(() => {
    const rawValue = searchParams.get('mapId');
    if (!rawValue) {
      return null;
    }

    const parsed = Number(rawValue);
    return Number.isNaN(parsed) ? null : parsed;
  }, [searchParams]);

  const selectedCampaign = useMemo(
    () => campaigns.find((campaign) => campaign.id === selectedCampaignId) ?? null,
    [campaigns, selectedCampaignId]
  );

  const battleMaps = campaignState?.battle_maps ?? [];
  const battleMapDetailsById = useMemo(
    () => new Map(battleMapDetails.map((battleMap) => [battleMap.id, battleMap])),
    [battleMapDetails]
  );
  const selectedBattleMap =
    battleMaps.find((battleMap) => battleMap.id === selectedMapId) ??
    (battleMaps.length === 1 ? battleMaps[0] : null);
  const selectedToken = useMemo(() => {
    if (!selectedBattleMap || selectedTokenId === null) {
      return null;
    }

    const tokenEntry = selectedBattleMap.tokens.find((token) => token.id === selectedTokenId) ?? null;
    return tokenEntry ? resolveTokenViewModel(tokenEntry, campaignState) : null;
  }, [campaignState, selectedBattleMap, selectedTokenId]);

  const cellSize = useMemo(() => {
    if (!selectedBattleMap) {
      return 36;
    }

    const availableWidth = Math.max(boardWidth - 32, 240);
    const widthFit = Math.floor(availableWidth / selectedBattleMap.width);
    return clamp(widthFit || 36, 24, 56);
  }, [boardWidth, selectedBattleMap]);

  useEffect(() => {
    let isActive = true;

    async function loadCampaigns() {
      setCampaignsLoading(true);
      setError(null);

      try {
        const { data } = await getCampaigns();

        if (!isActive) {
          return;
        }

        setCampaigns(data);
      } catch (requestError) {
        if (!isActive) {
          return;
        }

        setError(getApiErrorMessage(requestError, 'Не удалось загрузить список кампаний.'));
      } finally {
        if (isActive) {
          setCampaignsLoading(false);
        }
      }
    }

    void loadCampaigns();

    return () => {
      isActive = false;
    };
  }, []);

  useEffect(() => {
    if (campaigns.length !== 1) {
      return;
    }

    if (selectedCampaignId === campaigns[0].id) {
      return;
    }

    const nextParams = new URLSearchParams(searchParams);
    nextParams.set('campaignId', String(campaigns[0].id));
    nextParams.delete('mapId');
    setSearchParams(nextParams, { replace: true });
  }, [campaigns, searchParams, selectedCampaignId, setSearchParams]);

  useEffect(() => {
    let isActive = true;

    async function loadCampaignData() {
      if (!selectedCampaignId) {
        if (isActive) {
          setCampaignState(null);
          setBattleMapDetails([]);
          setCampaignLoading(false);
          setMoveError(null);
          setSelectedTokenId(null);
          setDragState(null);
          dragStateRef.current = null;
        }

        return;
      }

      if (isActive) {
        setCampaignLoading(true);
        setError(null);
        setMoveError(null);
        setSelectedTokenId(null);
        setDragState(null);
        dragStateRef.current = null;
        setCampaignState(null);
        setBattleMapDetails([]);
      }

      try {
        const [stateResponse, battleMapsResponse] = await Promise.allSettled([
          getCampaignState(selectedCampaignId),
          getCampaignBattleMaps(selectedCampaignId),
        ]);

        if (stateResponse.status === 'rejected') {
          throw stateResponse.reason;
        }

        if (!isActive) {
          return;
        }

        setCampaignState(stateResponse.value.data);
        setBattleMapDetails(battleMapsResponse.status === 'fulfilled' ? battleMapsResponse.value.data : []);
      } catch (requestError) {
        if (!isActive) {
          return;
        }

        setCampaignState(null);
        setBattleMapDetails([]);
        setError(getApiErrorMessage(requestError, 'Не удалось загрузить боевую карту.'));
      } finally {
        if (isActive) {
          setCampaignLoading(false);
        }
      }
    }

    void loadCampaignData();

    return () => {
      isActive = false;
    };
  }, [selectedCampaignId]);

  useEffect(() => {
    if (!selectedCampaignId || !campaignState) {
      return;
    }

    const campaignMapIds = campaignState.battle_maps.map((battleMap) => battleMap.id);

    if (campaignMapIds.length === 0) {
      if (selectedMapId !== null) {
        const nextParams = new URLSearchParams(searchParams);
        nextParams.delete('mapId');
        setSearchParams(nextParams, { replace: true });
      }
      return;
    }

    if (campaignMapIds.length === 1 && selectedMapId !== campaignMapIds[0]) {
      const nextParams = new URLSearchParams(searchParams);
      nextParams.set('campaignId', String(selectedCampaignId));
      nextParams.set('mapId', String(campaignMapIds[0]));
      setSearchParams(nextParams, { replace: true });
      return;
    }

    if (selectedMapId !== null && !campaignMapIds.includes(selectedMapId)) {
      const nextParams = new URLSearchParams(searchParams);
      nextParams.set('campaignId', String(selectedCampaignId));
      nextParams.set('mapId', String(campaignMapIds[0]));
      setSearchParams(nextParams, { replace: true });
    }
  }, [campaignState, selectedCampaignId, selectedMapId, searchParams, setSearchParams]);

  useEffect(() => {
    if (!selectedCampaignId || !token) {
      setConnectionStatus('disconnected');
      return;
    }

    const connection = connectCampaignWebSocket({
      campaignId: selectedCampaignId,
      token,
      onOpen: () => setConnectionStatus('connected'),
      onClose: (event) => {
        if (event.code === 1000 || event.code === 1008) {
          setConnectionStatus('disconnected');
          return;
        }

        setConnectionStatus('reconnecting');
      },
      onError: () => {
        setConnectionStatus('disconnected');
      },
      onMessage: (message: CampaignWebSocketEvent) => {
        const payload = isRecord(message.data) ? message.data : {};

        if (message.type === 'token_moved') {
          const tokenId = getNumberValue(payload.token_id);
          const x = getNumberValue(payload.x);
          const y = getNumberValue(payload.y);

          if (tokenId !== null && x !== null && y !== null) {
            setCampaignState((currentState) => updateTokenPosition(currentState, tokenId, x, y));
          }
        }
      },
    });

    return () => {
      connection.close();
      setConnectionStatus('disconnected');
    };
  }, [selectedCampaignId, token]);

  useEffect(() => {
    if (!selectedBattleMap) {
      setSelectedTokenId(null);
      setDragState(null);
      dragStateRef.current = null;
    }
  }, [selectedBattleMap]);

  useEffect(() => {
    const handleResize = () => {
      setBoardWidth(boardScrollRef.current?.clientWidth ?? 0);
    };

    handleResize();

    const observer = new ResizeObserver(handleResize);
    if (boardScrollRef.current) {
      observer.observe(boardScrollRef.current);
    }

    window.addEventListener('resize', handleResize);

    return () => {
      observer.disconnect();
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  useEffect(() => {
    if (!dragState || !selectedBattleMap || !isDm) {
      return;
    }

    const updateDragPosition = (clientX: number, clientY: number) => {
      const boardElement = boardScrollRef.current;
      if (!boardElement) {
        return;
      }

      const rect = boardElement.getBoundingClientRect();
      const nextX = clamp(Math.floor((clientX - rect.left) / cellSize), 0, selectedBattleMap.width - 1);
      const nextY = clamp(Math.floor((clientY - rect.top) / cellSize), 0, selectedBattleMap.height - 1);
      const nextState = { ...dragStateRef.current!, x: nextX, y: nextY };

      dragStateRef.current = nextState;
      setDragState(nextState);
    };

    const handlePointerMove = (event: PointerEvent) => {
      event.preventDefault();
      updateDragPosition(event.clientX, event.clientY);
    };

    const finishDrag = async () => {
      const currentDrag = dragStateRef.current;

      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
      window.removeEventListener('pointercancel', handlePointerUp);

      if (!currentDrag) {
        return;
      }

      const originalToken = selectedBattleMap.tokens.find((tokenEntry) => tokenEntry.id === currentDrag.tokenId);

      dragStateRef.current = null;
      setDragState(null);

      if (!originalToken || (originalToken.x === currentDrag.x && originalToken.y === currentDrag.y)) {
        return;
      }

      try {
        await moveBattleToken(currentDrag.tokenId, { x: currentDrag.x, y: currentDrag.y });
      } catch (requestError) {
        setMoveError(getApiErrorMessage(requestError, 'Не удалось переместить токен.'));
      }
    };

    const handlePointerUp = () => {
      void finishDrag();
    };

    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);
    window.addEventListener('pointercancel', handlePointerUp);

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
      window.removeEventListener('pointercancel', handlePointerUp);
    };
  }, [cellSize, dragState?.tokenId, isDm, selectedBattleMap]);

  const handleSelectCampaign = (campaignIdValue: number) => {
    const nextParams = new URLSearchParams(searchParams);
    nextParams.set('campaignId', String(campaignIdValue));
    nextParams.delete('mapId');
    setSearchParams(nextParams, { replace: true });
  };

  const handleSelectMap = (mapId: number) => {
    if (selectedCampaignId === null) {
      return;
    }

    const nextParams = new URLSearchParams(searchParams);
    nextParams.set('campaignId', String(selectedCampaignId));
    nextParams.set('mapId', String(mapId));
    setSearchParams(nextParams, { replace: true });
  };

  const startDraggingToken = (event: ReactPointerEvent<HTMLButtonElement>, tokenEntry: TokenViewModel) => {
    if (!isDm || !selectedBattleMap) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();

    const nextDragState = {
      tokenId: tokenEntry.id,
      x: tokenEntry.x,
      y: tokenEntry.y,
    };

    dragStateRef.current = nextDragState;
    setDragState(nextDragState);
    setMoveError(null);
    setSelectedTokenId(tokenEntry.id);
  };

  const renderCampaignChooser = () => {
    if (campaignsLoading) {
      return (
        <Paper variant="outlined" sx={{ p: 3 }}>
          <Stack spacing={1.5}>
            <Typography variant="h5">Battle Maps</Typography>
            <Typography color="text.secondary">Загружаем доступные кампании...</Typography>
          </Stack>
        </Paper>
      );
    }

    if (campaigns.length === 0) {
      return (
        <Paper variant="outlined" sx={{ p: 3 }}>
          <Stack spacing={1.5}>
            <Typography variant="h5">Battle Maps</Typography>
            <Typography color="text.secondary">Нет доступных кампаний.</Typography>
          </Stack>
        </Paper>
      );
    }

    return (
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Stack spacing={2}>
          <Box>
            <Typography variant="h5">Battle Maps</Typography>
            <Typography color="text.secondary">
              Выберите кампанию, чтобы открыть её боевые карты.
            </Typography>
          </Box>
          <Stack spacing={1.25}>
            {campaigns.map((campaign) => (
              <Card
                key={campaign.id}
                variant="outlined"
                sx={{
                  borderColor: selectedCampaignId === campaign.id ? 'primary.main' : 'divider',
                  bgcolor: selectedCampaignId === campaign.id ? alpha('#2563eb', 0.06) : 'background.paper',
                }}
              >
                <CardContent sx={{ '&:last-child': { pb: 2 } }}>
                  <Stack direction={{ xs: 'column', sm: 'row' }} alignItems={{ sm: 'center' }} spacing={1.5}>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography variant="subtitle1" noWrap>
                        {campaign.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {campaign.description || 'Описание не указано'}
                      </Typography>
                    </Box>
                    <Button variant="contained" onClick={() => handleSelectCampaign(campaign.id)}>
                      Open
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Stack>
      </Paper>
    );
  };

  const renderBoard = () => {
    if (!selectedCampaignId) {
      return null;
    }

    if (campaignLoading) {
      return (
        <Paper variant="outlined" sx={{ p: 3, flex: 1, minWidth: 0 }}>
          <Typography color="text.secondary">Загружаем боевую карту...</Typography>
        </Paper>
      );
    }

    if (!campaignState) {
      return null;
    }

    if (!selectedBattleMap) {
      return (
        <Paper variant="outlined" sx={{ p: 3, flex: 1, minWidth: 0 }}>
          <Stack spacing={2}>
            <Box>
              <Typography variant="h6">Нет выбранной карты</Typography>
              <Typography color="text.secondary">
                {battleMaps.length > 1
                  ? 'Выберите одну из доступных карт ниже.'
                  : 'В этой кампании пока нет боевых карт.'}
              </Typography>
            </Box>

            {battleMaps.length > 1 ? (
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {battleMaps.map((battleMap) => {
                  const details = battleMapDetailsById.get(battleMap.id);
                  return (
                    <Button
                      key={battleMap.id}
                      variant="outlined"
                      onClick={() => handleSelectMap(battleMap.id)}
                      sx={{ textTransform: 'none' }}
                    >
                      {details?.name ?? `#${battleMap.id}`} ({battleMap.width}x{battleMap.height})
                    </Button>
                  );
                })}
              </Stack>
            ) : null}
          </Stack>
        </Paper>
      );
    }

    const displayedTokens = selectedBattleMap.tokens
      .map((tokenEntry) => {
        if (dragState?.tokenId === tokenEntry.id) {
          return {
            token: tokenEntry,
            view: {
              ...resolveTokenViewModel(tokenEntry, campaignState),
              x: dragState.x,
              y: dragState.y,
            },
          };
        }

        return {
          token: tokenEntry,
          view: resolveTokenViewModel(tokenEntry, campaignState),
        };
      })
      .filter(Boolean);

    return (
      <Paper
        variant="outlined"
        sx={{
          flex: 1,
          minWidth: 0,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          bgcolor: 'background.paper',
        }}
      >
        <Box sx={{ p: 2.25, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Stack spacing={1.25}>
            <Box
              sx={{
                display: 'flex',
                alignItems: { xs: 'flex-start', sm: 'center' },
                justifyContent: 'space-between',
                gap: 2,
                flexDirection: { xs: 'column', sm: 'row' },
              }}
            >
              <Box sx={{ minWidth: 0 }}>
                <Typography variant="h5" noWrap>
                  {resolveBattleMapName(selectedBattleMap, battleMapDetailsById)}
                </Typography>
                <Typography color="text.secondary" noWrap>
                  {selectedBattleMap.width} x {selectedBattleMap.height} grid
                </Typography>
              </Box>
              <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                <Chip
                  size="small"
                  color={connectionStatus === 'connected' ? 'success' : connectionStatus === 'reconnecting' ? 'warning' : 'default'}
                  label={
                    connectionStatus === 'connected'
                      ? 'WebSocket: connected'
                      : connectionStatus === 'reconnecting'
                        ? 'WebSocket: reconnecting'
                        : 'WebSocket: offline'
                  }
                />
                <Chip size="small" label={isDm ? 'DM mode' : 'Player mode'} />
                <Button
                  component={RouterLink}
                  to={`/campaign/${selectedCampaignId}`}
                  variant="outlined"
                  size="small"
                >
                  Campaign
                </Button>
              </Stack>
            </Box>

            {battleMaps.length > 1 ? (
              <Stack spacing={1}>
                <Typography variant="body2" color="text.secondary">
                  Доступные карты
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {battleMaps.map((battleMap) => {
                    const details = battleMapDetailsById.get(battleMap.id);
                    const active = battleMap.id === selectedBattleMap.id;
                    return (
                      <Button
                        key={battleMap.id}
                        variant={active ? 'contained' : 'outlined'}
                        color={active ? 'primary' : 'inherit'}
                        size="small"
                        onClick={() => handleSelectMap(battleMap.id)}
                        sx={{ textTransform: 'none' }}
                      >
                        {details?.name ?? `#${battleMap.id}`} ({battleMap.width}x{battleMap.height})
                      </Button>
                    );
                  })}
                </Stack>
              </Stack>
            ) : null}
          </Stack>
        </Box>

        {moveError ? (
          <Box sx={{ px: 2, pt: 2 }}>
            <Alert severity="error" onClose={() => setMoveError(null)}>
              {moveError}
            </Alert>
          </Box>
        ) : null}

        <Box
          ref={boardScrollRef}
          sx={{
            flex: 1,
            minHeight: 0,
            overflow: 'auto',
            p: 2,
            bgcolor: 'background.default',
            backgroundImage:
              'radial-gradient(circle at 1px 1px, rgba(148, 163, 184, 0.2) 1px, transparent 0)',
            backgroundSize: '18px 18px',
          }}
        >
          <Box
            sx={{
              position: 'relative',
              display: 'inline-block',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2,
              overflow: 'hidden',
              boxShadow: '0 10px 35px rgba(15, 23, 42, 0.12)',
              bgcolor: 'rgba(255,255,255,0.72)',
              backdropFilter: 'blur(6px)',
            }}
          >
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: `repeat(${selectedBattleMap.width}, ${cellSize}px)`,
                gridTemplateRows: `repeat(${selectedBattleMap.height}, ${cellSize}px)`,
              }}
            >
              {Array.from({ length: selectedBattleMap.width * selectedBattleMap.height }, (_, index) => {
                const x = index % selectedBattleMap.width;
                const y = Math.floor(index / selectedBattleMap.width);
                return (
                  <Box
                    key={`${x}-${y}`}
                    sx={{
                      width: `${cellSize}px`,
                      height: `${cellSize}px`,
                      borderRight: '1px solid',
                      borderBottom: '1px solid',
                      borderColor: 'rgba(148, 163, 184, 0.32)',
                      bgcolor: (x + y) % 2 === 0 ? 'rgba(248, 250, 252, 0.92)' : 'rgba(241, 245, 249, 0.92)',
                    }}
                  />
                );
              })}
            </Box>

            <Box
              sx={{
                position: 'absolute',
                inset: 0,
              }}
            >
              {displayedTokens.map(({ view }) => {
                const selected = selectedTokenId === view.id;
                const tooltipTitle = (
                  <Stack spacing={0.25}>
                    <Typography variant="body2" sx={{ fontWeight: 700 }}>
                      {view.name}
                    </Typography>
                    <Typography variant="caption">
                      Coordinates: {view.x}, {view.y}
                    </Typography>
                  </Stack>
                );

                return (
                  <Tooltip key={view.id} title={tooltipTitle} arrow placement="top">
                    <Box
                      component="button"
                      type="button"
                      onPointerDown={(event) => {
                        if (dragStateRef.current && dragStateRef.current.tokenId !== view.id) {
                          return;
                        }

                        if (isDm && selectedBattleMap) {
                          startDraggingToken(event, view);
                          return;
                        }

                        setSelectedTokenId(view.id);
                      }}
                      onClick={() => setSelectedTokenId(view.id)}
                      sx={{
                        position: 'absolute',
                        left: `${view.x * cellSize + 2}px`,
                        top: `${view.y * cellSize + 2}px`,
                        width: `${cellSize - 4}px`,
                        height: `${cellSize - 4}px`,
                        borderRadius: 1.5,
                        border: '1px solid',
                        borderColor: selected ? alpha(view.color, 0.95) : alpha(view.color, 0.48),
                        backgroundColor: alpha(view.color, selected ? 0.2 : 0.12),
                        boxShadow: selected
                          ? `0 0 0 2px ${alpha(view.color, 0.18)}, 0 12px 24px ${alpha(view.color, 0.18)}`
                          : `0 6px 18px ${alpha(view.color, 0.12)}`,
                        color: '#0f172a',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.75,
                        px: 1,
                        cursor: isDm ? (dragState?.tokenId === view.id ? 'grabbing' : 'grab') : 'pointer',
                        userSelect: 'none',
                        transition: 'transform 120ms ease, box-shadow 120ms ease, background-color 120ms ease',
                        zIndex: selected ? 3 : 2,
                        '&:hover': {
                          transform: 'translateY(-1px)',
                        },
                        '&:focus-visible': {
                          outline: '2px solid',
                          outlineColor: alpha(view.color, 0.95),
                          outlineOffset: 2,
                        },
                      }}
                    >
                      <Box
                        sx={{
                          width: 10,
                          height: 10,
                          borderRadius: '50%',
                          bgcolor: view.color,
                          flexShrink: 0,
                        }}
                      />
                      <Box sx={{ minWidth: 0, textAlign: 'left' }}>
                        <Typography variant="caption" component="div" noWrap sx={{ fontWeight: 700, lineHeight: 1.1 }}>
                          {view.name}
                        </Typography>
                        <Typography variant="caption" component="div" noWrap sx={{ lineHeight: 1.1, opacity: 0.8 }}>
                          {view.x}, {view.y}
                        </Typography>
                      </Box>
                    </Box>
                  </Tooltip>
                );
              })}
            </Box>
          </Box>
        </Box>
      </Paper>
    );
  };

  const renderRightPanel = () => {
    return (
      <Paper
        variant="outlined"
        sx={{
          width: { xs: '100%', lg: 340 },
          flexShrink: 0,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <CardContent sx={{ flex: 1 }}>
          <Stack spacing={2}>
            <Box>
              <Typography variant="h6">Token details</Typography>
              <Typography variant="body2" color="text.secondary">
                Наведите курсор на токен или выберите его, чтобы увидеть подробности.
              </Typography>
            </Box>

            <Divider />

            {selectedToken ? (
              <Stack spacing={1.25}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Name
                  </Typography>
                  <Typography variant="subtitle1">{selectedToken.name}</Typography>
                </Box>

                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Type
                  </Typography>
                  <Typography variant="body1">
                    {selectedToken.kind === 'character'
                      ? 'Character'
                      : selectedToken.kind === 'monster'
                        ? 'Monster'
                        : 'Token'}
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="caption" color="text.secondary">
                    HP
                  </Typography>
                  <Typography variant="body1">{selectedToken.hpLabel ?? '—'}</Typography>
                </Box>

                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Coordinates
                  </Typography>
                  <Typography variant="body1">
                    {selectedToken.x}, {selectedToken.y}
                  </Typography>
                </Box>

                <Chip
                  label={selectedToken.kind === 'character' ? 'Blue' : selectedToken.kind === 'monster' ? 'Red' : 'Neutral'}
                  sx={{
                    width: 'fit-content',
                    bgcolor:
                      selectedToken.kind === 'character'
                        ? alpha('#2563eb', 0.12)
                        : selectedToken.kind === 'monster'
                          ? alpha('#dc2626', 0.12)
                          : alpha('#64748b', 0.12),
                  }}
                />
              </Stack>
            ) : (
              <Typography color="text.secondary">
                {selectedBattleMap
                  ? 'Выберите токен на карте.'
                  : 'Сначала выберите кампанию и боевую карту.'}
              </Typography>
            )}

            <Divider />

            <Stack spacing={1}>
              <Typography variant="subtitle2">Legend</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip size="small" label="Characters" sx={{ bgcolor: alpha('#2563eb', 0.12) }} />
                <Chip size="small" label="Monsters" sx={{ bgcolor: alpha('#dc2626', 0.12) }} />
              </Stack>
            </Stack>

            <Divider />

            <Stack spacing={1}>
              <Typography variant="subtitle2">Controls</Typography>
              <Typography variant="body2" color="text.secondary">
                {isDm
                  ? 'DM может перетаскивать токены мышью и выпускать их на новой клетке.'
                  : 'Player только наблюдает. Перемещение недоступно.'}
              </Typography>
            </Stack>
          </Stack>
        </CardContent>
      </Paper>
    );
  };

  if (error) {
    return (
      <Stack spacing={2}>
        <Alert severity="error">{error}</Alert>
        <Button component={RouterLink} to="/dashboard" variant="outlined" sx={{ width: 'fit-content' }}>
          Back to Dashboard
        </Button>
      </Stack>
    );
  }

  return (
    <Stack spacing={2.5} sx={{ minHeight: 'calc(100vh - 160px)' }}>
      <Stack spacing={0.75}>
        <Typography variant="h4" component="h1">
          Battle
        </Typography>
        <Typography color="text.secondary">
          Interactive battle map with live token updates over WebSocket.
        </Typography>
      </Stack>

      {selectedCampaign ? (
        <Paper variant="outlined" sx={{ p: 2.25 }}>
          <Stack spacing={1.25}>
            <Box
              sx={{
                display: 'flex',
                alignItems: { xs: 'flex-start', sm: 'center' },
                justifyContent: 'space-between',
                gap: 2,
                flexDirection: { xs: 'column', sm: 'row' },
              }}
            >
              <Box sx={{ minWidth: 0 }}>
                <Typography variant="h6" noWrap>
                  {selectedCampaign.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" noWrap>
                  {selectedCampaign.description || 'Описание не указано'}
                </Typography>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip size="small" label={`Campaign #${selectedCampaign.id}`} />
              </Stack>
            </Box>
            <Alert severity="info" variant="outlined">
              {isDm
                ? 'DM: drag tokens to move them. The board updates when the websocket event arrives.'
                : 'Player: the board updates live when tokens move. No refresh needed.'}
            </Alert>
          </Stack>
        </Paper>
      ) : null}

      {selectedCampaignId === null ? renderCampaignChooser() : null}

      {selectedCampaignId !== null ? (
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            flex: 1,
            minHeight: 0,
            alignItems: 'stretch',
            flexDirection: { xs: 'column', lg: 'row' },
          }}
        >
          {renderBoard()}
          {renderRightPanel()}
        </Box>
      ) : null}

      {campaignLoading && selectedCampaignId ? (
        <Typography color="text.secondary">Loading campaign state...</Typography>
      ) : null}

      {!campaignLoading && selectedCampaignId && !selectedBattleMap && campaignState && campaignState.battle_maps.length > 1 ? (
        <Alert severity="info">Выберите одну из доступных карт, чтобы открыть её.</Alert>
      ) : null}

      {!campaignLoading && selectedCampaignId && campaignState && campaignState.battle_maps.length === 0 ? (
        <Alert severity="warning">В этой кампании пока нет боевых карт.</Alert>
      ) : null}
    </Stack>
  );
}
