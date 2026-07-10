import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { createCampaign, getCampaigns } from '../api/campaigns';
import { PageShell } from '../components/PageShell';
import { getApiErrorMessage } from '../lib/apiError';
import { useAuth } from '../hooks/useAuth';
import type { Campaign } from '../types/campaign';

export function DashboardPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [createName, setCreateName] = useState('');
  const [createDescription, setCreateDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { user } = useAuth();
  const isDm = user?.role === 'dm';

  useEffect(() => {
    let isActive = true;

    async function loadCampaigns() {
      setIsLoading(true);
      setError(null);

      try {
        const { data } = await getCampaigns();

        if (isActive) {
          setCampaigns(data);
        }
      } catch (requestError) {
        if (isActive) {
          setError(getApiErrorMessage(requestError, 'Не удалось загрузить кампании.'));
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    void loadCampaigns();

    return () => {
      isActive = false;
    };
  }, [reloadToken]);

  const openCreateDialog = () => {
    setCreateName('');
    setCreateDescription('');
    setCreateError(null);
    setIsCreateDialogOpen(true);
  };

  const handleCreateCampaign = async () => {
    setIsCreating(true);
    setCreateError(null);

    try {
      await createCampaign({
        name: createName.trim(),
        description: createDescription.trim(),
      });
      setIsCreateDialogOpen(false);
      setReloadToken((value) => value + 1);
    } catch (requestError) {
      setCreateError(getApiErrorMessage(requestError, 'Не удалось создать кампанию.'));
    } finally {
      setIsCreating(false);
    }
  };

  const renderContent = () => {
    if (error) {
      return <Alert severity="error">{error}</Alert>;
    }

    if (isLoading) {
      return (
        <Stack spacing={2}>
          <Paper sx={{ p: 3, opacity: 0.72 }}>
            <Typography variant="body1" color="text.secondary">
              Loading your campaigns...
            </Typography>
          </Paper>
          <Paper sx={{ p: 3, opacity: 0.72 }}>
            <Typography variant="body1" color="text.secondary">
              Loading your campaigns...
            </Typography>
          </Paper>
        </Stack>
      );
    }

    if (campaigns.length === 0) {
      return (
        <Card variant="outlined" sx={{ borderStyle: 'dashed' }}>
          <CardContent>
            <Stack spacing={1}>
              <Typography variant="h6">У вас пока нет кампаний.</Typography>
              <Typography color="text.secondary">
                Когда вы будете добавлены в кампанию или создадите свою, она появится здесь.
              </Typography>
            </Stack>
          </CardContent>
        </Card>
      );
    }

    return (
      <Stack spacing={2}>
        {campaigns.map((campaign) => {
          const participantCount =
            campaign.participant_count ?? campaign.participants_count ?? campaign.members_count;
          const dmLabel = user && campaign.dm_id === user.id ? 'Вы' : `#${campaign.dm_id}`;

          return (
            <Card key={campaign.id} variant="outlined">
              <CardContent>
                <Stack spacing={1.5}>
                  <Box
                    sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 2 }}
                  >
                    <Box>
                      <Typography variant="h6" component="h2">
                        {campaign.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                        {campaign.description || 'Описание не указано'}
                      </Typography>
                    </Box>
                    <Chip size="small" label={`Campaign #${campaign.id}`} />
                  </Box>
                  <Divider />
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
                    <Typography variant="body2" color="text.secondary">
                      DM: {dmLabel}
                    </Typography>
                    {typeof participantCount === 'number' ? (
                      <Typography variant="body2" color="text.secondary">
                        Участников: {participantCount}
                      </Typography>
                    ) : null}
                  </Stack>
                </Stack>
              </CardContent>
              <CardActions sx={{ px: 2, pb: 2 }}>
                <Button variant="contained" onClick={() => navigate(`/campaign/${campaign.id}`)}>
                  Open
                </Button>
              </CardActions>
            </Card>
          );
        })}
      </Stack>
    );
  };

  return (
    <PageShell title="Dashboard">
      <Stack spacing={2}>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={2}
          alignItems={{ sm: 'center' }}
          justifyContent="space-between"
        >
          <Typography color="text.secondary">
            {user ? `Добро пожаловать, ${user.email}.` : 'Добро пожаловать.'}
          </Typography>
          {isDm ? (
            <Button variant="contained" onClick={openCreateDialog}>
              Create Campaign
            </Button>
          ) : null}
        </Stack>

        <Box>{renderContent()}</Box>
      </Stack>

      <Dialog open={isCreateDialogOpen} onClose={() => setIsCreateDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Create Campaign</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            {createError ? <Alert severity="error">{createError}</Alert> : null}
            <TextField
              label="Название"
              value={createName}
              onChange={(event) => setCreateName(event.target.value)}
              fullWidth
              autoFocus
            />
            <TextField
              label="Описание"
              value={createDescription}
              onChange={(event) => setCreateDescription(event.target.value)}
              fullWidth
              multiline
              minRows={3}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsCreateDialogOpen(false)} disabled={isCreating}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateCampaign}
            disabled={isCreating || createName.trim().length === 0}
          >
            {isCreating ? 'Saving...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
