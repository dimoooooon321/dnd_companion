import { useState, type FormEvent } from 'react';
import { Alert, Button, Paper, Stack, TextField, Typography } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { login as loginRequest, getCurrentUser } from '../api/auth';
import { getApiErrorMessage } from '../lib/apiError';
import { PageShell } from '../components/PageShell';
import { useAuth } from '../hooks/useAuth';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const { data: authResponse } = await loginRequest({ email, password });
      const { data: user } = await getCurrentUser(authResponse.access_token);

      login({
        token: authResponse.access_token,
        user,
      });

      navigate('/dashboard', { replace: true });
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось войти в систему.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageShell title="Login">
      <Typography variant="body1" color="text.secondary">
        Sign in to continue to your campaign dashboard.
      </Typography>
      <Paper sx={{ p: 3, mt: 2, maxWidth: 480 }}>
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            {error ? <Alert severity="error">{error}</Alert> : null}
            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              fullWidth
              autoComplete="email"
            />
            <TextField
              label="Password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              fullWidth
              autoComplete="current-password"
            />
            <Button type="submit" variant="contained" size="large" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Login'}
            </Button>
            <Button component={RouterLink} to="/register" variant="text">
              Create account
            </Button>
          </Stack>
        </form>
      </Paper>
    </PageShell>
  );
}
