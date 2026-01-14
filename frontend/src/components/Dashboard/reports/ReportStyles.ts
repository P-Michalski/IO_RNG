import { StyleSheet } from "@react-pdf/renderer";

export const styles = StyleSheet.create({
  // Page
  page: {
    flexDirection: "column",
    backgroundColor: "#FFFFFF",
    padding: 40,
    fontFamily: "Helvetica",
  },

  // Header
  header: {
    marginBottom: 30,
    paddingBottom: 15,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 12,
    color: "#64748b",
    marginBottom: 4,
  },
  metadata: {
    fontSize: 10,
    color: "#94a3b8",
    marginTop: 8,
  },

  // Sections
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#1e293b",
    marginBottom: 12,
    borderBottom: "1 solid #e2e8f0",
    paddingBottom: 6,
  },
  sectionSubtitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#475569",
    marginTop: 15,
    marginBottom: 8,
  },

  // Summary cards
  summaryGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
    marginBottom: 20,
  },
  summaryCard: {
    flex: 1,
    minWidth: "45%",
    backgroundColor: "#f8fafc",
    border: "1 solid #e2e8f0",
    borderRadius: 6,
    padding: 12,
  },
  summaryLabel: {
    fontSize: 10,
    color: "#64748b",
    marginBottom: 4,
    textTransform: "uppercase",
  },
  summaryValue: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#0f172a",
  },
  summarySubValue: {
    fontSize: 10,
    color: "#64748b",
    marginTop: 2,
  },

  // Tables
  table: {
    display: "flex",
    width: "100%",
    marginVertical: 10,
  },
  tableHeader: {
    flexDirection: "row",
    paddingVertical: 8,
    paddingHorizontal: 10,
  },
  tableRow: {
    flexDirection: "row",
    borderBottom: "1 solid #e2e8f0",
    paddingVertical: 8,
    paddingHorizontal: 10,
  },
  tableRowAlt: {
    flexDirection: "row",
    backgroundColor: "#f8fafc",
    borderBottom: "1 solid #e2e8f0",
    paddingVertical: 8,
    paddingHorizontal: 10,
  },
  tableCell: {
    fontSize: 10,
    color: "#334155",
    flex: 1,
  },
  tableCellHeader: {
    fontSize: 10,
    fontWeight: "bold",
    color: "#0f172a",
    flex: 1,
  },
  tableCellRight: {
    fontSize: 10,
    color: "#334155",
    flex: 1,
    textAlign: "right",
  },

  // Charts/Images
  chartContainer: {
    marginVertical: 15,
    alignItems: "center",
  },
  chartImage: {
    maxWidth: "100%",
    maxHeight: 250,
    objectFit: "contain",
  },
  chartCaption: {
    fontSize: 10,
    color: "#64748b",
    marginTop: 8,
    textAlign: "center",
  },

  // Status badges
  badgeSuccess: {
    backgroundColor: "#dcfce7",
    color: "#166534",
    fontSize: 9,
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 3,
  },
  badgeDanger: {
    backgroundColor: "#fee2e2",
    color: "#991b1b",
    fontSize: 9,
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 3,
  },
  badgeWarning: {
    backgroundColor: "#fef3c7",
    color: "#92400e",
    fontSize: 9,
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 3,
  },

  // Progress bar
  progressBarContainer: {
    width: "100%",
    height: 8,
    backgroundColor: "#e2e8f0",
    borderRadius: 4,
    overflow: "hidden",
    marginVertical: 6,
  },
  progressBarFill: {
    height: "100%",
  },

  // Footer
  footer: {
    position: "absolute",
    bottom: 30,
    left: 40,
    right: 40,
    fontSize: 8,
    color: "#94a3b8",
    textAlign: "center",
    borderTop: "1 solid #e2e8f0",
    paddingTop: 10,
  },

  // Text styles
  textBold: {
    fontWeight: "bold",
  },
  textMuted: {
    color: "#64748b",
  },
  textSmall: {
    fontSize: 9,
  },
  textCenter: {
    textAlign: "center",
  },

  // Spacing
  mt1: { marginTop: 4 },
  mt2: { marginTop: 8 },
  mt3: { marginTop: 12 },
  mb1: { marginBottom: 4 },
  mb2: { marginBottom: 8 },
  mb3: { marginBottom: 12 },

  // Page break
  pageBreak: {
    marginTop: 20,
  },

  // Chart legend
  chartLegend: {
    flexDirection: "row",
    gap: 16,
    marginTop: 8,
    paddingHorizontal: 8,
    paddingVertical: 6,
    backgroundColor: "#f8fafc",
    borderRadius: 4,
  },
  legendItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  legendBox: {
    width: 12,
    height: 12,
    borderRadius: 2,
  },
  legendText: {
    fontSize: 9,
    color: "#475569",
  },
});
