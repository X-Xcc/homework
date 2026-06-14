import { AppProvider } from './app/providers/AppProvider';
import { router } from './app/router';
import { RouterProvider } from 'react-router-dom';

export function App() {
  return (
    <AppProvider>
      <RouterProvider router={router} />
    </AppProvider>
  );
}
