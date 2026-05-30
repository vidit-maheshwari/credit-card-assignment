import { useState, useEffect } from 'react';
import { getAvailableMonths, getMonthlyAnalytics } from '../api';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = [
  '#18181b', '#3f3f46', '#71717a', '#a1a1aa', '#2563eb',
  '#0891b2', '#059669', '#ca8a04', '#dc2626', '#9333ea',
  '#e11d48', '#0d9488'
];

export default function Dashboard() {
  const [months, setMonths] = useState([]);
  const [selectedMonth, setSelectedMonth] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMonths();
  }, []);

  useEffect(() => {
    if (selectedMonth) {
      loadAnalytics(selectedMonth);
    }
  }, [selectedMonth]);

  const loadMonths = async () => {
    try {
      const res = await getAvailableMonths();
      setMonths(res.data.months);
      if (res.data.months.length > 0) {
        setSelectedMonth(res.data.months[res.data.months.length - 1]);
      }
    } catch (err) {
      console.error('Failed to load months:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async (month) => {
    setLoading(true);
    try {
      const res = await getMonthlyAnalytics(month);
      setAnalytics(res.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !analytics) {
    return <div className="loading"><div className="spinner"></div><p>Loading...</p></div>;
  }

  if (months.length === 0) {
    return (
      <div className="empty-state">
        <h2>No Data Yet</h2>
        <p>Go to the Statements tab to ingest your credit card statements.</p>
      </div>
    );
  }

  const categorySpendData = analytics
    ? Object.entries(analytics.category_spend).map(([name, value]) => ({ name, value }))
    : [];

  const categoryRewardsData = analytics
    ? Object.entries(analytics.category_rewards).map(([name, value]) => ({ name, value }))
    : [];

  return (
    <div>
      <div className="filter-bar">
        <select value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)}>
          {months.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>

      {analytics && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">₹{analytics.total_spend.toLocaleString()}</div>
              <div className="stat-label">Total Spend</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{analytics.total_rewards.toLocaleString()}</div>
              <div className="stat-label">Reward Points</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{analytics.transaction_count}</div>
              <div className="stat-label">Transactions</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{analytics.highest_reward_category || 'N/A'}</div>
              <div className="stat-label">Best Reward Category</div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="card">
              <h2>Spend by Category</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categorySpendData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    outerRadius={100}
                    dataKey="value"
                  >
                    {categorySpendData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <h2>Rewards by Category</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryRewardsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={11} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#18181b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h2>Category Breakdown</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Spend</th>
                    <th>Rewards</th>
                    <th>Reward Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(analytics.category_spend)
                    .sort(([, a], [, b]) => b - a)
                    .map(([cat, spend]) => (
                      <tr key={cat}>
                        <td><span className="category-pill">{cat}</span></td>
                        <td>₹{spend.toLocaleString()}</td>
                        <td>{(analytics.category_rewards[cat] || 0).toLocaleString()} pts</td>
                        <td>
                          {spend > 0
                            ? ((analytics.category_rewards[cat] || 0) / spend * 100).toFixed(2) + '%'
                            : '-'}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
