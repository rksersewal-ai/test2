/**
 * main.tsx — application entry point
 * SPRINT 3: Wrapped app in <ThemeProvider> (Feature #10)
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { TextScaleProvider } from './context/TextScaleContext';
import { ThemeProvider } from './context/ThemeContext';
import App from './App';
import './styles/global.css';
import './styles/tokens.css';
import './styles/components.css';
import './styles/dark-mode.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <TextScaleProvider>
          <ThemeProvider>
            <App />
          </ThemeProvider>
        </TextScaleProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
