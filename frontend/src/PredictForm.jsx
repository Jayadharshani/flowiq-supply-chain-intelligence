import { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000";

const DEFAULT_ORDER = {
  order_purchase_timestamp: "2018-05-14 10:30:00",
  order_estimated_delivery_date: "2018-05-25 00:00:00",
  customer_zip_code_prefix: 3149,
  customer_city: "sao paulo",
  customer_state: "SP",
  order_item_id: 1,
  price: 89.9,
  freight_value: 15.5,
  product_category_name: "utilidades_domesticas",
  product_name_lenght: 40,
  product_description_lenght: 268,
  product_photos_qty: 4,
  product_weight_g: 1200,
  product_length_cm: 20,
  product_height_cm: 10,
  product_width_cm: 15,
  payment_sequential: 1,
  payment_type: "credit_card",
  payment_installments: 3,
  payment_value: 105.4,
};

// Each step lists WHICH fields it shows. The form data itself
// (`order` state) is shared across all steps - only the visible
// fields change as currentStep changes.
const STEPS = [
  {
    title: "Order Timing",
    fields: ["order_purchase_timestamp", "order_estimated_delivery_date", "order_item_id"],
  },
  {
    title: "Customer Location",
    fields: ["customer_city", "customer_state", "customer_zip_code_prefix"],
  },
  {
    title: "Product Details",
    fields: [
      "product_category_name", "price", "freight_value", "product_weight_g",
      "product_length_cm", "product_height_cm", "product_width_cm",
      "product_name_lenght", "product_description_lenght", "product_photos_qty",
    ],
  },
  {
    title: "Payment",
    fields: ["payment_type", "payment_installments", "payment_sequential", "payment_value"],
  },
];

// Human-friendly labels for each field key
const LABELS = {
  order_purchase_timestamp: "Purchase Date/Time",
  order_estimated_delivery_date: "Estimated Delivery Date",
  order_item_id: "Item #",
  customer_city: "City",
  customer_state: "State",
  customer_zip_code_prefix: "Zip Prefix",
  product_category_name: "Category",
  price: "Price",
  freight_value: "Freight Value",
  product_weight_g: "Weight (g)",
  product_length_cm: "Length (cm)",
  product_height_cm: "Height (cm)",
  product_width_cm: "Width (cm)",
  product_name_lenght: "Name Length (chars)",
  product_description_lenght: "Description Length (chars)",
  product_photos_qty: "Photo Count",
  payment_type: "Payment Method",
  payment_installments: "Installments",
  payment_sequential: "Payment Sequence",
  payment_value: "Amount Paid",
};

const NUMBER_FIELDS = new Set([
  "customer_zip_code_prefix", "order_item_id", "price", "freight_value",
  "product_name_lenght", "product_description_lenght", "product_photos_qty",
  "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm",
  "payment_sequential", "payment_installments", "payment_value",
]);

// Fields shown as a dropdown (populated from /options) instead of
// free text - this is what fixes the "karaikal" problem, since the
// user can only pick a value the model actually learned from.
const DROPDOWN_FIELDS = new Set([
  "customer_city", "customer_state", "product_category_name", "payment_type",
]);

function PredictForm({ token, onLogout }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [order, setOrder] = useState(DEFAULT_ORDER);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [options, setOptions] = useState({}); // { customer_city: [...], customer_state: [...], ... }
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [sampleOrders, setSampleOrders] = useState([]);
  const [selectedSampleIndex, setSelectedSampleIndex] = useState("");

  const isLastStep = currentStep === STEPS.length - 1;

  function handleChange(e) {
    const { name, value } = e.target;
    setOrder((prev) => ({
      ...prev,
      [name]: NUMBER_FIELDS.has(name) ? parseFloat(value) || 0 : value,
    }));
  }

  function goNext() {
    setCurrentStep((s) => Math.min(s + 1, STEPS.length - 1));
  }

  function goBack() {
    setCurrentStep((s) => Math.max(s - 1, 0));
  }

  async function authedFetch(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    });
    if (response.status === 401) {
      // Token expired or invalid - send them back to login
      onLogout();
      throw new Error("Session expired, please log in again");
    }
    return response;
  }

  async function fetchHistory() {
    try {
      const response = await authedFetch(`${API_BASE}/history?limit=50`);
      const data = await response.json();
      setHistory(data);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await authedFetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(order),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Prediction failed");
      }

      const data = await response.json();
      setResult(data);
      fetchHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function fetchOptions() {
    try {
      const response = await authedFetch(`${API_BASE}/options`);
      const data = await response.json();
      setOptions(data);
    } catch (err) {
      console.error("Failed to load options:", err);
    } finally {
      setOptionsLoading(false);
    }
  }

  async function fetchSampleOrders() {
    try {
      const response = await authedFetch(`${API_BASE}/sample-orders`);
      const data = await response.json();
      setSampleOrders(data);
    } catch (err) {
      console.error("Failed to load sample orders:", err);
    }
  }

  function handleSampleSelect(e) {
    const index = e.target.value;
    setSelectedSampleIndex(index);
    if (index === "") return;
    // Load that real order's values into the form, replacing
    // whatever is currently filled in.
    setOrder(sampleOrders[parseInt(index, 10)]);
  }

  // Load history, valid dropdown options, and sample order templates
  // once when this component mounts
  useEffect(() => {
    fetchHistory();
    fetchOptions();
    fetchSampleOrders();
  }, []);

  const step = STEPS[currentStep];

  return (
    <div className="app">
      <header className="header">
        <div className="header-row">
          <div>
            <h1>FlowIQ</h1>
            <p>Supply Chain Delay Prediction Dashboard</p>
          </div>
          <button className="logout-btn" onClick={onLogout}>Logout</button>
        </div>
      </header>

      <section className="card">
        {/* Sample order picker - lets you load a real dataset order as a starting point */}
        {sampleOrders.length > 0 && (
          <label className="sample-picker">
            Load a real order from the dataset (optional)
            <select value={selectedSampleIndex} onChange={handleSampleSelect}>
              <option value="">-- Choose a sample order --</option>
              {sampleOrders.map((s, i) => (
                <option key={i} value={i}>
                  {s.customer_city} ({s.customer_state}) - {s.product_category_name} - ${s.price}
                </option>
              ))}
            </select>
          </label>
        )}

        {/* Step indicator */}
        <div className="step-indicator">
          {STEPS.map((s, i) => (
            <div key={s.title} className={`step-dot ${i === currentStep ? "active" : i < currentStep ? "done" : ""}`}>
              {i + 1}. {s.title}
            </div>
          ))}
        </div>

        <h2>{step.title}</h2>
        {optionsLoading && <p className="hint-text">Loading valid options...</p>}

        <form onSubmit={isLastStep ? handleSubmit : (e) => e.preventDefault()} className="form-grid">
          {step.fields.map((field) => (
            <label key={field} className="field-label">
              {LABELS[field]}
              {DROPDOWN_FIELDS.has(field) ? (
                <select
                  name={field}
                  value={order[field]}
                  onChange={handleChange}
                  disabled={optionsLoading}
                >
                  {(options[field] || []).map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : (
                <input
                  type={NUMBER_FIELDS.has(field) ? "number" : "text"}
                  step={NUMBER_FIELDS.has(field) ? "0.01" : undefined}
                  name={field}
                  value={order[field]}
                  onChange={handleChange}
                />
              )}
            </label>
          ))}

          <div className="step-nav">
            {currentStep > 0 && (
              <button type="button" onClick={goBack} className="back-btn">Back</button>
            )}
            {!isLastStep && (
              <button type="button" onClick={goNext} className="next-btn">Next</button>
            )}
            {isLastStep && (
              <button type="submit" disabled={loading} className="predict-btn">
                {loading ? "Predicting..." : "Predict Delay"}
              </button>
            )}
          </div>
        </form>

        {error && <p className="error">Error: {error}</p>}

        {result && (
          <div className={`result-box risk-${result.risk_level.toLowerCase()}`}>
            <span className="risk-badge">{result.risk_level} RISK</span>
            <p>Predicted: <strong>{result.late_delivery_predicted ? "LATE" : "ON TIME"}</strong></p>
            <p>Delay Probability: <strong>{(result.late_probability * 100).toFixed(1)}%</strong></p>
            {result.warning && <p className="warning-text">{result.warning}</p>}
          </div>
        )}
      </section>

      <section className="kpi-row">
        <div className="kpi-card">
          <span className="kpi-value">{history.length}</span>
          <span className="kpi-label">Total Predictions</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-value">{history.filter((h) => h.late_delivery_predicted).length}</span>
          <span className="kpi-label">Predicted Late</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-value">
            {history.length > 0
              ? ((history.filter((h) => h.risk_level === "HIGH").length / history.length) * 100).toFixed(1)
              : "0.0"}%
          </span>
          <span className="kpi-label">High Risk Rate</span>
        </div>
      </section>

      <section className="card">
        <h2>Your Recent Predictions</h2>
        <table className="history-table">
          <thead>
            <tr>
              <th>City</th><th>State</th><th>Category</th><th>Price</th><th>Risk</th><th>Late?</th>
            </tr>
          </thead>
          <tbody>
            {history.map((row) => (
              <tr key={row.id}>
                <td>{row.customer_city}</td>
                <td>{row.customer_state}</td>
                <td>{row.product_category_name}</td>
                <td>${row.price.toFixed(2)}</td>
                <td><span className={`badge risk-${row.risk_level.toLowerCase()}`}>{row.risk_level}</span></td>
                <td>{row.late_delivery_predicted ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {history.length === 0 && <p>No predictions yet.</p>}
      </section>
    </div>
  );
}

export default PredictForm;

 
