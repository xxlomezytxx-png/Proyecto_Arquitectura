import PricingDashboard from "../components/pricing/PricingDashboard";

const PreciosPage = () => {
  return (
    <>
      <h1>Panel de Pricing</h1>
      <p style={{ marginBottom: "20px", color: "#6b7280" }}>
        Gestión de precios en tiempo real
      </p>

      <PricingDashboard />
    </>
  );
};

export default PreciosPage;