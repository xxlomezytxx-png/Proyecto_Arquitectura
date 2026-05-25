import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

interface HistoryItem {
  price: number;
  date: string;
}

interface Props {
  history: HistoryItem[];
}

const PricingChart = ({ history }: Props) => {
  const chartData = history
    .slice()
    .reverse()
    .map((item) => ({
      fecha: item.date,
      precio: item.price,
    }));

  return (
    <div style={{ width: "100%", height: 250 }}>
      <ResponsiveContainer>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="fecha" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="precio" stroke="#2563eb" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PricingChart;