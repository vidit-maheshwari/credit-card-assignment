import { useState } from 'react';
import Dashboard from './components/Dashboard';
import Transactions from './components/Transactions';
import Trends from './components/Trends';
import Chat from './components/Chat';
import Statements from './components/Statements';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'transactions', label: 'Transactions' },
    { id: 'trends', label: 'Trends' },
    { id: 'chat', label: 'Ask Agent' },
    { id: 'statements', label: 'Statements' },
  ];

  return (
    <div className="app">
      <header className="app-header">
        <h1>Credit Card Spend Analytics</h1>
        <nav className="tab-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>
      <main className="app-main">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'transactions' && <Transactions />}
        {activeTab === 'trends' && <Trends />}
        {activeTab === 'chat' && <Chat />}
        {activeTab === 'statements' && <Statements />}
      </main>
    </div>
  );
}

export default App;
