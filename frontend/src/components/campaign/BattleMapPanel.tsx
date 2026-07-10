import { Card, CardContent, Chip, Grid, Skeleton, Stack, Typography } from '@mui/material';
import type { CampaignBattleMapDetails, CampaignBattleMapState } from '../../types/campaignState';

type BattleMapPanelProps = {
  battleMaps: CampaignBattleMapState[];
  battleMapDetailsById: Map<number, CampaignBattleMapDetails>;
  isLoading: boolean;
};

function findBattleMapName(
  battleMap: CampaignBattleMapState,
  battleMapDetailsById: Map<number, CampaignBattleMapDetails>
) {
  return battleMapDetailsById.get(battleMap.id)?.name ?? `Боевая карта #${battleMap.id}`;
}

export function BattleMapPanel({ battleMaps, battleMapDetailsById, isLoading }: BattleMapPanelProps) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="h6">Боевые карты</Typography>
          {isLoading && battleMaps.length === 0 ? (
            <Stack spacing={1.5}>
              <Skeleton variant="rounded" height={108} />
              <Skeleton variant="rounded" height={108} />
            </Stack>
          ) : battleMaps.length ? (
            <Grid container spacing={2}>
              {battleMaps.map((battleMap) => (
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
                        {battleMap.tokens.length ? (
                          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                            {battleMap.tokens.map((token) => (
                              <Chip
                                key={token.id}
                                size="small"
                                label={`#${token.id} (${token.x}, ${token.y})`}
                              />
                            ))}
                          </Stack>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            Токенов нет
                          </Typography>
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography color="text.secondary">Боевые карты отсутствуют.</Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
