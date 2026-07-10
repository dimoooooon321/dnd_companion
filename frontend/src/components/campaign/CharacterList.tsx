import { Card, CardContent, Grid, Skeleton, Stack, Typography } from '@mui/material';
import type { CampaignCharacterState } from '../../types/campaignState';

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

type CharacterListProps = {
  characters: CampaignCharacterState[];
  isLoading: boolean;
};

function formatAbilityScores(character: CampaignCharacterState) {
  const chips = ABILITY_SCORE_LABELS.map(({ key, label }) => ({ label, value: character[key] })).filter(
    (entry): entry is { label: string; value: number } => typeof entry.value === 'number'
  );

  if (chips.length === 0) {
    return 'Характеристики не передаются текущим API.';
  }

  return chips.map((entry) => `${entry.label} ${entry.value}`).join('  ');
}

export function CharacterList({ characters, isLoading }: CharacterListProps) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="h6">Персонажи</Typography>
          {isLoading && characters.length === 0 ? (
            <Stack spacing={1.5}>
              <Skeleton variant="rounded" height={88} />
              <Skeleton variant="rounded" height={88} />
            </Stack>
          ) : characters.length ? (
            <Grid container spacing={2}>
              {characters.map((character) => (
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
              ))}
            </Grid>
          ) : (
            <Typography color="text.secondary">В кампании пока нет персонажей</Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
