import { createBrowserRouter } from 'react-router-dom';
import Layout from '@components/Layout';
import HomePage from '@pages/HomePage';
import TradesPage from '@pages/TradesPage';
import PositionsPage from '@pages/PositionsPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'trades',
        element: <TradesPage />,
      },
      {
        path: 'positions',
        element: <PositionsPage />,
      },
    ],
  },
]);

