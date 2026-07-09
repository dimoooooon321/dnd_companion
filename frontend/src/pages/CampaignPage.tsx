import { useEffect, useRef, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { getCampaignBattleMaps, getCampaignState } from '../api/campaigns';
import { PageShell } from '../components/PageShell';
import { getApiErrorMessage } from '../lib/apiError';
import type {
  CampaignBattleMapDetails,
  CampaignBattleMapState,
  CampaignCharacterState,
  CampaignEventState,
  CampaignState,
} from '../types/campaignState';

const ABILITY_SCORE_LABELS: Array<{
  key: keyof Pick<
    CampaignCharacterState,
    'strength' | 'dexterity' | 'constitution' | 'intelligence' | 'wisdom' | 'charisma'
  >;
  label: string;
}> = [
  { key: 'strength', label: 'STR' },
  { key: 'dexterity', label: 'DEX' },
  { key: 'constitution', label: 'CON' },
  { key: 'intelligence', label: 'INT' },
  { key: 'wisdom', label: 'WIS' },
  { key: 'charisma', label: 'CHA' },
];

const EVENT_TYPE_LABELS: Record<string, string> = {
  monster_added: 'Monster added',
  hp_updated: 'HP updated',
  inventory_updated: 'Inventory updated',
  scene_changed: 'Scene changed',
  system: 'System',
};

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

function formatLabelFromType(type: string) {
  return EVENT_TYPE_LABELS[type] ?? type.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatEventDetails(event: CampaignEventState) {
  const textValue = event.data.text;

  if (typeof textValue === 'string' && textValue.trim().length > 0) {
    return textValue;
  }

  const entries = Object.entries(event.data);

  if (entries.length === 0) {
    return 'Дополнительные данные отсутствуют.';
  }

  return entries
    .map(([key, value]) => `${key}: ${typeof value === 'string' ? value : JSON.stringify(value)}`)
    .join(' • ');
}

function formatAbilityScores(character: CampaignCharacterState) {
  const chips = ABILITY_SCORE_LABELS
    .map(({ key, label }) => ({ label, value: character[key] }))
    .filter((entry): entry is { label: string; value: number } => typeof entry.value === 'number');

  if (chips.length === 0) {
    return 'Характеристики не передаются текущим API.';
  }

  return chips.map((entry) => `${entry.label} ${entry.value}`).join('  ');
}

function findBattleMapName(
  battleMap: CampaignBattleMapState,
  battleMapDetailsById: Map<number, CampaignBattleMapDetails>,
) {
  return battleMapDetailsById.get(battleMap.id)?.name ?? `Боевая карта #${battleMap.id}`;
}

export function CampaignPage() {
  const { campaignId } = useParams();
  const [campaignState, setCampaignState] = useState<CampaignState | null>(null);
  const [battleMapDetails, setBattleMapDetails] = useState<CampaignBattleMapDetails[]>([]);
  const [isLoading, setIsLoading] = useState(Boolean(campaignId));
  const [error, setError] = useState<string | null>(null);
  const isMountedRef = useRef(true);

  async function loadCampaignState(parsedCampaignId: number) {
    setIsLoading(true);
    setError(null);

    try {
      const [stateResult, battleMapsResult] = await Promise.allSettled([
        getCampaignState(parsedCampaignId),
        getCampaignBattleMaps(parsedCampaignId),
      ]);

      if (stateResult.status === 'rejected') {
        throw stateResult.reason;
      }

      if (!isMountedRef.current) {
        return;
      }

      setCampaignState(stateResult.value.data);

      if (battleMapsResult.status === 'fulfilled') {
        setBattleMapDetails(battleMapsResult.value.data);
      } else {
        setBattleMapDetails([]);
      }
    } catch (requestError) {
      if (!isMountedRef.current) {
        return;
      }

      setCampaignState(null);
      setBattleMapDetails([]);
      setError(getApiErrorMessage(requestError, 'Не удалось загрузить state кампании.'));
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }

  useEffect(() => {
    isMountedRef.current = true;

    if (!campaignId) {
      setCampaignState(null);
      setBattleMapDetails([]);
      setIsLoading(false);
      setError(null);
      return;
    }

    const parsedCampaignId = Number(campaignId);

    if (Number.isNaN(parsedCampaignId)) {
      setCampaignState(null);
      setBattleMapDetails([]);
      setIsLoading(false);
      setError('Некорректный идентификатор кампании.');
      return;
    }

    void loadCampaignState(parsedCampaignId);

    return () => {
      isMountedRef.current = false;
    };
  }, [campaignId]);

  if (!campaignId) {
    return (
      <PageShell title="Campaign">
        <Paper variant="outlined" sx={{ p: 3 }}>
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
        </Paper>
      </PageShell>
    );
  }

  const parsedCampaignId = Number(campaignId);
  const activeCampaign = campaignState?.campaign ?? null;
  const participantsCount = campaignState?.characters.length ?? 0;
  const battleMapDetailsById = new Map(battleMapDetails.map((battleMap) => [battleMap.id, battleMap]));
  const visibleEvents = campaignState ? [...campaignState.recent_events].reverse() : [];

  return (
    <PageShell title="Campaign">
      {error ? <Alert severity="error">{error}</Alert> : null}

      <Stack spacing={2}>
        <Card variant="outlined">
          <CardContent>
            <Stack spacing={1.5}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 2 }}>
                <Box>
                  <Typography variant="h5" component="h2">
                    {activeCampaign?.name ?? `Campaign #${parsedCampaignId}`}
                  </Typography>
                  <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                    {activeCampaign?.description || 'Описание не указано'}
                  </Typography>
                </Box>
                <Chip label={`Campaign #${parsedCampaignId}`} />
              </Box>

              <Divider />

              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    DM
                  </Typography>
                  <Typography variant="body1">{activeCampaign ? `#${activeCampaign.dm_id}` : '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Участники
                  </Typography>
                  <Typography variant="body1">{participantsCount}</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Campaign ID
                  </Typography>
                  <Typography variant="body1">{parsedCampaignId}</Typography>
                </Grid>
              </Grid>

              <Box>
                <Button variant="outlined" onClick={() => void loadCampaignState(parsedCampaignId)} disabled={isLoading}>
                  Refresh
                </Button>
              </Box>
            </Stack>
          </CardContent>
        </Card>

        {isLoading && !campaignState ? (
          <Typography color="text.secondary">Loading campaign state...</Typography>
        ) : null}

        <Card variant="outlined">
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="h6">Персонажи</Typography>
              <Grid container spacing={2}>
                {campaignState?.characters.length ? (
                  campaignState.characters.map((character) => (
                    <Grid item xs={12} sm={6} lg={4} key={character.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Stack spacing={1}>
                            <Typography variant="subtitle1">{character.name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {character.race} · {character.class_name} · Level {character.level}
                            </Typography>
                            <Typography variant="body2">
                              HP: {character.current_hp}/{character.max_hp}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {formatAbilityScores(character)}
                            </Typography>
                          </Stack>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))
                ) : (
                  <Grid item xs={12}>
                    <Typography color="text.secondary">Персонажи отсутствуют.</Typography>
                  </Grid>
                )}
              </Grid>
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="h6">Монстры</Typography>
              <Grid container spacing={2}>
                {campaignState?.monsters.length ? (
                  campaignState.monsters.map((campaignMonster) => (
                    <Grid item xs={12} sm={6} lg={4} key={campaignMonster.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Stack spacing={1}>
                            <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 1 }}>
                              <Typography variant="subtitle1">{campaignMonster.monster.name}</Typography>
                              <Chip size="small" label={`x${campaignMonster.quantity}`} />
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                              HP: {campaignMonster.monster.hp}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              CR: {campaignMonster.monster.challenge_rating}
                            </Typography>
                            <Typography variant="body2">
                              {campaignMonster.monster.description || 'Описание отсутствует.'}
                            </Typography>
                          </Stack>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))
                ) : (
                  <Grid item xs={12}>
                    <Typography color="text.secondary">Монстры отсутствуют.</Typography>
                  </Grid>
                )}
              </Grid>
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="h6">Активная сцена</Typography>
              {campaignState?.current_scene ? (
                <Card variant="outlined">
                  <CardContent>
                    <Stack spacing={1}>
                      <Typography variant="subtitle1">{campaignState.current_scene.title}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {campaignState.current_scene.description}
                      </Typography>
                    </Stack>
                  </CardContent>
                </Card>
              ) : (
                <Typography color="text.secondary">Активная сцена отсутствует</Typography>
              )}
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="h6">История событий</Typography>
              <Stack spacing={1.5}>
                {visibleEvents.length ? (
                  visibleEvents.map((event) => (
                    <Card key={event.id} variant="outlined">
                      <CardContent>
                        <Stack spacing={0.75}>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1 }}>
                            <Chip size="small" label={formatLabelFromType(event.type)} />
                            <Typography variant="caption" color="text.secondary">
                              {formatDateTime(event.created_at)}
                            </Typography>
                          </Box>
                          <Typography variant="body2">{formatEventDetails(event)}</Typography>
                        </Stack>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <Typography color="text.secondary">События отсутствуют.</Typography>
                )}
              </Stack>
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="h6">Боевая карта</Typography>
              <Grid container spacing={2}>
                {campaignState?.battle_maps.length ? (
                  campaignState.battle_maps.map((battleMap) => (
                    <Grid item xs={12} sm={6} lg={4} key={battleMap.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Stack spacing={1}>
                            <Typography variant="subtitle1">
                              {findBattleMapName(battleMap, battleMapDetailsById)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Размер: {battleMap.width} x {battleMap.height}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Токенов: {battleMap.tokens.length}
                            </Typography>
                          </Stack>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))
                ) : (
                  <Grid item xs={12}>
                    <Typography color="text.secondary">Боевые карты отсутствуют.</Typography>
                  </Grid>
                )}
              </Grid>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </PageShell>
  );
}
