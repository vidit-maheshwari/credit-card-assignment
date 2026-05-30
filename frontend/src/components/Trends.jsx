import { useState, useEffect } from 'react';
import { getTrends, getAvailableMonths } from '../api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, BarChart, Bar
} from 'recharts';

const COLORS = [
  '#18181b', '#3f3f46', '#71717a', '#a1a1aa', '#2563eb',
  '#0891b2', '#059669', '#ca8a04', '#dc2626', '#9333ea'
];

export default function Trends() {
  const [trends, setTrends] = useState(null);
  const [months, setMonths] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const monthsRes = await getAvailableMonths();
      setMonths(monthsRes.data.months);

      const trendsRes = await getTrends();
      setTrends(trendsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div><p>Loading trends...</p></div>;
  }

  if (!trends || trends.months.length === 0) {
    return (
      <div className="empty-state">
        <h2>No Trend Data</h2>
        <p>Need at least one month of data to show trends.</p>
      </div>
    );
  }

  // Prepare total spend/rewards trend data
  const totalTrendData = trends.months.map((month, i) => ({
    month,
    spend: trends.total_spend_trend[i],
    rewards: trends.total_rewards_trend[i],
    spendChange: trends.mom_spend_change[i],
    rewardsChange: trends.mom_rewards_change[i],
  }));

  // Prepare category spend data for stacked bar chart
  const categorySpendData = trends.months.map((month) => {
    const entry = { month };
    Object.keys(trends.spend_by_category).forEach((cat) => {
      const catData = trends.spend_by_category[cat].find((d) => d.month === month);
      entry[cat] = catData ? catData.amount : 0;
    });
    return entry;
  });

  const allCategories = Object.keys(trends.spend_by_category);

  return (
    <div>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{trends.months.length}</div>
          <div className="stat-label">Months of Data</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            ₹{trends.total_spend_trend.reduce((a, b) => a + b, 0).toLocaleString()}
          </div>
          <div className="stat-label">Total Spend (All Months)</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {trends.total_rewards_trend.reduce((a, b) => a + b, 0).toLocaleString()}
          </div>
          <div className="stat-label">Total Rewards (All Months)</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="card">
          <h2>Total Spend Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={totalTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
              <Legend />
              <Line type="monotone" dataKey="spend" stroke="#18181b" strokeWidth={2} name="Spend (₹)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2>Rewards Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={totalTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="rewards" stroke="#18181b" strokeWidth={2} name="Rewards (pts)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h2>Spend by Category (Monthly)</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={categorySpendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
            <Legend />
            {allCategories.map((cat, i) => (
              <Bar key={cat} dataKey={cat} stackId="a" fill={COLORS[i % COLORS.length]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2>Month-over-Month Changes</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Month</th>
                <th>Total Spend</th>
                <th>Spend Change</th>
                <th>Total Rewards</th>
                <th>Rewards Change</th>
                <th>Top Reward Category</th>
              </tr>
            </thead>
            <tbody>
              {totalTrendData.map((row) => (
                <tr key={row.month}>
                  <td>{row.month}</td>
                  <td>₹{row.spend.toLocaleString()}</td>
                  <td style={{ color: row.spendChange > 0 ? 'var(--danger)' : row.spendChange < 0 ? 'var(--success)' : 'inherit' }}>
                    {row.spendChange !== null ? `${row.spendChange > 0 ? '+' : ''}${row.spendChange}%` : '-'}
                  </td>
                  <td>{row.rewards.toLocaleString()} pts</td>
                  <td style={{ color: row.rewardsChange > 0 ? 'var(--success)' : row.rewardsChange < 0 ? 'var(--danger)' : 'inherit' }}>
                    {row.rewardsChange !== null ? `${row.rewardsChange > 0 ? '+' : ''}${row.rewardsChange}%` : '-'}
                  </td>
                  <td>{trends.highest_reward_category_trend[trends.months.indexOf(row.month)] || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
