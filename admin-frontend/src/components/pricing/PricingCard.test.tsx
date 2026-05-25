import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PricingCard from "./PricingCard";
import PricingDashboard from "./PricingDashboard";
import PricingExplanation from "./PricingExplanation";
import {
  getPricingList,
  recalculatePrice,
  getBookDetail,
} from "../../services/pricingService";

vi.mock("../../services/pricingService", () => ({
  getPricingList: vi.fn(),
  bulkCalculate: vi.fn(),
  recalculatePrice: vi.fn(),
  getBookDetail: vi.fn(),
  getPriceHistory: vi.fn(),
  getCatalogProducts: vi.fn().mockResolvedValue([]),
  getReports: vi.fn(),
  getConfig: vi.fn(),
  saveConfig: vi.fn(),
}));

const mockItem = {
  book_id: "book-1",
  title: "Libro de Prueba",
  condition: "BUENO",
  price: 15.0,
  isFallback: false,
};

const mockFallbackItem = {
  book_id: "book-2",
  title: "Libro Estimado",
  condition: "ACEPTABLE",
  price: 8.0,
  isFallback: true,
};

test("PricingDashboard renders table with pricing data", async () => {
  vi.mocked(getPricingList).mockResolvedValue([
    {
      book_id: "book-1",
      title: "Libro de Prueba",
      condition: "BUENO",
      suggested_price: 15.0,
      is_fallback: false,
    },
  ]);

  render(<PricingDashboard />);

  await waitFor(() => {
    expect(screen.getByText("Libro de Prueba")).toBeInTheDocument();
  });

  expect(screen.getByRole("columnheader", { name: "Título" })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: "Condición" })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: "Precio" })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: "Fuente" })).toBeInTheDocument();
});

test("PricingCard shows fallback badge when source is internal", () => {
  render(<PricingCard data={mockFallbackItem} />);
  expect(screen.getByText("Estimado")).toBeInTheDocument();
});

test("RecalculateButton shows loading state during request", async () => {
  vi.mocked(recalculatePrice).mockImplementation(
    () => new Promise((resolve) => setTimeout(resolve, 5000))
  );

  render(<PricingCard data={mockItem} />);

  fireEvent.click(screen.getByText("Recalcular"));

  expect(await screen.findByText("Calculando…")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Calculando…" })).toBeDisabled();
});

test("PricingExplanation displays breakdown correctly", async () => {
  vi.mocked(getBookDetail).mockResolvedValue({
    suggested_price: 12.5,
    base_price: 16.67,
    condition_factor: 0.75,
    source: "ebay",
    references_used: 3,
    explanation: "Precio calculado con 3 referencias de eBay.",
    is_fallback: false,
  });

  render(<PricingExplanation bookId="book-1" />);

  await waitFor(() => {
    expect(screen.getByText("Desglose del cálculo")).toBeInTheDocument();
  });

  expect(screen.getByText("$16.67")).toBeInTheDocument();
  expect(screen.getByText("0.75")).toBeInTheDocument();
  expect(
    screen.getByText("Precio calculado con 3 referencias de eBay.")
  ).toBeInTheDocument();
});

test("Error state renders user-friendly message", async () => {
  vi.mocked(recalculatePrice).mockRejectedValue(new Error("Network error"));

  render(<PricingCard data={mockItem} />);

  fireEvent.click(screen.getByText("Recalcular"));

  await waitFor(() => {
    expect(
      screen.getByText("No se pudo recalcular el precio. Intente de nuevo.")
    ).toBeInTheDocument();
  });
});
