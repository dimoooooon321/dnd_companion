import { Box, Button, Card, CardContent, Chip, Divider, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { Campaign } from '../../types/campaign';

type CampaignHeaderProps = {
  campaign: Campaign | null;
  campaignId: number;
  participantCount: number;
  dmLabel: string;
  connectionStatus: 'connected' | 'disconnected' | 'connecting' | 'reconnecting';
  isLoading: boolean;
  onRefresh: () => void;
};

export function CampaignHeader({
  campaign,
  campaignId,
  participantCount,
  dmLabel,
  connectionStatus,
  isLoading,
  onRefresh,
}: CampaignHeaderProps) {
  const connectionLabel =
    connectionStatus === 'connected'
      ? 'Live'
      : connectionStatus === 'connecting'
        ? 'Connecting'
        : connectionStatus === 'reconnecting'
          ? 'Reconnecting'
          : 'Offline';

  const connectionColor =
    connectionStatus === 'connected'
      ? 'success'
      : connectionStatus === 'connecting'
        ? 'warning'
        : connectionStatus === 'reconnecting'
          ? 'warning'
          : 'error';

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={1.5}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              gap: 2,
            }}
          >
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography variant="h5" component="h2">
                {campaign?.name ?? `Campaign #${campaignId}`}
              </Typography>
              <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                {campaign?.description || 'Описание не указано'}
              </Typography>
              <Chip
                size="small"
                color={connectionColor}
                label={connectionLabel}
                sx={{ width: 'fit-content', mt: 0.25 }}
              />
            </Box>
            <Chip label={`Campaign #${campaignId}`} />
          </Box>

          <Divider />

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                DM
              </Typography>
              <Typography variant="body1">{campaign ? dmLabel : '—'}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Участники
              </Typography>
              <Typography variant="body1">{participantCount}</Typography>
            </Box>
            <Box sx={{ ml: { sm: 'auto' } }}>
              <Stack direction="row" spacing={1}>
                <Button component={RouterLink} to={`/battle?campaignId=${campaignId}`} variant="outlined">
                  Battle
                </Button>
                <Button variant="outlined" onClick={onRefresh} disabled={isLoading}>
                  {isLoading ? 'Refreshing...' : 'Refresh'}
                </Button>
              </Stack>
            </Box>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
