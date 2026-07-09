import { Box, Paper, Typography } from '@mui/material';
import type { ReactNode } from 'react';

type PageShellProps = {
  title: string;
  children?: ReactNode;
};

export function PageShell({ title, children }: PageShellProps) {
  return (
    <Paper elevation={0} sx={{ p: { xs: 2, md: 3 }, border: '1px solid', borderColor: 'divider' }}>
      <Box sx={{ display: 'grid', gap: 1.5 }}>
        <Typography variant="h4" component="h1">
          {title}
        </Typography>
        {children}
      </Box>
    </Paper>
  );
}
