import { Card, CardContent, Chip, Skeleton, Stack, Typography } from '@mui/material';
import type { CampaignEventState } from '../../types/campaignState';

type EventListProps = {
  events: CampaignEventState[];
  isLoading: boolean;
};

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

export function EventList({ events, isLoading }: EventListProps) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="h6">История событий</Typography>
          {isLoading && events.length === 0 ? (
            <Stack spacing={1.5}>
              <Skeleton variant="rounded" height={84} />
              <Skeleton variant="rounded" height={84} />
            </Stack>
          ) : events.length ? (
            <Stack spacing={1.5}>
              {events.map((event) => (
                <Card key={event.id} variant="outlined">
                  <CardContent>
                    <Stack spacing={0.75}>
                      <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1}>
                        <Chip size="small" label={formatLabelFromType(event.type)} />
                        <Typography variant="caption" color="text.secondary">
                          {formatDateTime(event.created_at)}
                        </Typography>
                      </Stack>
                      <Typography variant="body2">{formatEventDetails(event)}</Typography>
                    </Stack>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          ) : (
            <Typography color="text.secondary">События отсутствуют.</Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
