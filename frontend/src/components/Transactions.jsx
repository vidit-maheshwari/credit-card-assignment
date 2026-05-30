import { useState, useEffect } from 'react';
import { getTransactions, getAvailableMonths } from '../api';

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [months, setMonths] = useState([]);
  const [filters, setFilters] = useState({ month: '', category: '', bank: '' });
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const limit = 50;

  useEffect(() => {
    loadMonths();
  }, []);

  useEffect(() => {
    loadTransactions();
  }, [filters, page]);

  const loadMonths = async () => {
    try {
      const res = await getAvailableMonths();
      setMonths(res.data.months);
    } catch (err) {
      console.error(err);
    }
  };

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const params = {
        limit,
        offset: page * limit,
        ...(filters.month && { month: filters.month }),
        ...(filters.category && { category: filters.category }),
        ...(filters.bank && { bank: filters.bank }),
      };
      const res = await getTransactions(params);
      setTransactions(res.data.transactions);
      setTotal(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    'Dining', 'Travel', 'Groceries', 'Fuel', 'Utilities',
    'Shopping', 'Entertainment', 'Rent', 'Healthcare', 'Education',
    'Insurance', 'EMI', 'Other'
  ];

  const banks = ['HDFC', 'ICICI', 'SBI', 'Axis'];

  return (
    <div>
      <div className="filter-bar">
        <select
          value={filters.month}
          onChange={(e) => { setFilters({ ...filters, month: e.target.value }); setPage(0); }}
        >
          <option value="">All Months</option>
          {months.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
        <select
          value={filters.category}
          onChange={(e) => { setFilters({ ...filters, category: e.target.value }); setPage(0); }}
        >
          <option value="">All Categories</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select
          value={filters.bank}
          onChange={(e) => { setFilters({ ...filters, bank: e.target.value }); setPage(0); }}
        >
          <option value="">All Banks</option>
          {banks.map((b) => <option key={b} value={b}>{b}</option>)}
        </select>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          {total} transactions found
        </span>
      </div>

      {loading ? (
        <div className="loading"><div className="spinner"></div></div>
      ) : transactions.length === 0 ? (
        <div className="empty-state">
          <p>No transactions found. Try adjusting filters or ingest statements first.</p>
        </div>
      ) : (
        <>
          <div className="card">
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Merchant</th>
                    <th>Amount</th>
                    <th>Type</th>
                    <th>Category</th>
                    <th>Rewards</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((txn) => (
                    <tr key={txn.id}>
                      <td>{txn.transaction_date}</td>
                      <td>{txn.merchant_description}</td>
                      <td>₹{txn.amount.toLocaleString()}</td>
                      <td>
                        <span className={`badge badge-${txn.transaction_type}`}>
                          {txn.transaction_type}
                        </span>
                      </td>
                      <td><span className="category-pill">{txn.category}</span></td>
                      <td>{txn.reward_points || 0} pts</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="filter-bar" style={{ justifyContent: 'center' }}>
            <button
              className="btn btn-primary"
              disabled={page === 0}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </button>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Page {page + 1} of {Math.ceil(total / limit)}
            </span>
            <button
              className="btn btn-primary"
              disabled={(page + 1) * limit >= total}
              onClick={() => setPage(page + 1)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
