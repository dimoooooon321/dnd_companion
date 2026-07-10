import { Card, CardContent, Chip, Grid, Skeleton, Stack, Typography } from '@mui/material';
import type { CampaignMonsterState } from '../../types/campaignState';

type MonsterListProps = {
  monsters: CampaignMonsterState[];
  isLoading: boolean;
};

export function MonsterList({ monsters, isLoading }: MonsterListProps) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="h6">Монстры</Typography>
          {isLoading && monsters.length === 0 ? (
            <Stack spacing={1.5}>
              <Skeleton variant="rounded" height={88} />
              <Skeleton variant="rounded" height={88} />
            </Stack>
          ) : monsters.length ? (
            <Grid container spacing={2}>
              {monsters.map((campaignMonster) => (
                <Grid item xs={12} sm={6} lg={4} key={campaignMonster.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Stack spacing={1}>
                        <Stack direction="row" spacing={1} alignItems="flex-start" justifyContent="space-between">
                          <Typography variant="subtitle1">{campaignMonster.monster.name}</Typography>
                          <Chip size="small" label={`x${campaignMonster.quantity}`} />
                        </Stack>
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
              ))}
            </Grid>
          ) : (
            <Typography color="text.secondary">Бестиарий пуст</Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
