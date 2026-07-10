import { Card, CardContent, Chip, Grid, Skeleton, Stack, Typography } from '@mui/material';
import type { CampaignSceneState } from '../../types/campaignState';

type ScenePanelProps = {
  currentScene: CampaignSceneState | null;
  scenes: CampaignSceneState[];
  isLoading: boolean;
};

export function ScenePanel({ currentScene, scenes, isLoading }: ScenePanelProps) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="h6">Сцены</Typography>
          {isLoading && scenes.length === 0 && !currentScene ? (
            <Stack spacing={1.5}>
              <Skeleton variant="rounded" height={108} />
              <Skeleton variant="rounded" height={108} />
            </Stack>
          ) : (
            <>
              <Stack spacing={1.5}>
                <Typography variant="subtitle1">Активная сцена</Typography>
                {currentScene ? (
                  <Card variant="outlined">
                    <CardContent>
                      <Stack spacing={1}>
                        <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1}>
                          <Typography variant="subtitle1">{currentScene.title}</Typography>
                          <Chip size="small" color={currentScene.is_active ? 'success' : 'default'} label="Active" />
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                          {currentScene.description}
                        </Typography>
                      </Stack>
                    </CardContent>
                  </Card>
                ) : (
                  <Typography color="text.secondary">Активная сцена отсутствует</Typography>
                )}
              </Stack>

              <Stack spacing={1.5}>
                <Typography variant="subtitle1">Все сцены</Typography>
                {scenes.length ? (
                  <Grid container spacing={2}>
                    {scenes.map((scene) => (
                      <Grid item xs={12} sm={6} lg={4} key={scene.id}>
                        <Card variant="outlined">
                          <CardContent>
                            <Stack spacing={1}>
                              <Stack direction="row" justifyContent="space-between" spacing={1}>
                                <Typography variant="subtitle2">{scene.title}</Typography>
                                <Chip
                                  size="small"
                                  color={scene.is_active ? 'success' : 'default'}
                                  label={scene.is_active ? 'Active' : 'Inactive'}
                                />
                              </Stack>
                              <Typography variant="body2" color="text.secondary">
                                {scene.description}
                              </Typography>
                            </Stack>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Typography color="text.secondary">Сцены отсутствуют.</Typography>
                )}
              </Stack>
            </>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
