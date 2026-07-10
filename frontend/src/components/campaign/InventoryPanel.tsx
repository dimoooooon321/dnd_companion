import { Card, CardContent, Chip, Grid, Skeleton, Stack, Typography } from '@mui/material';
import type { CampaignCharacterState } from '../../types/campaignState';
import type { CharacterInventoryItem } from '../../types/inventory';

type InventoryPanelProps = {
  characters: CampaignCharacterState[];
  inventoriesByCharacterId: Record<number, CharacterInventoryItem[]>;
  isLoading: boolean;
};

function formatItemLabel(item: CharacterInventoryItem) {
  return `${item.item.name} x${item.quantity}`;
}

export function InventoryPanel({ characters, inventoriesByCharacterId, isLoading }: InventoryPanelProps) {
  const isInventoryLoading = isLoading && Object.keys(inventoriesByCharacterId).length === 0;

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="h6">Инвентарь</Typography>
          {isInventoryLoading ? (
            <Stack spacing={1.5}>
              <Skeleton variant="rounded" height={88} />
              <Skeleton variant="rounded" height={88} />
            </Stack>
          ) : characters.length ? (
            <Grid container spacing={2}>
              {characters.map((character) => {
                const inventory = inventoriesByCharacterId[character.id] ?? [];

                return (
                  <Grid item xs={12} sm={6} lg={4} key={character.id}>
                    <Card variant="outlined">
                      <CardContent>
                        <Stack spacing={1}>
                          <Typography variant="subtitle1">{character.name}</Typography>
                          {inventory.length ? (
                            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                              {inventory.map((entry) => (
                                <Chip key={entry.id} size="small" label={formatItemLabel(entry)} />
                              ))}
                            </Stack>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              Предметов нет
                            </Typography>
                          )}
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          ) : (
            <Typography color="text.secondary">Персонажи отсутствуют.</Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
