/**
 * Utility function to convert chart (SVG/Canvas) to base64 image
 * This is used to embed charts in PDF reports
 */

import domtoimage from "dom-to-image-more";

export interface ChartExportOptions {
  scale?: number; // Higher scale = better quality (default: 2)
  backgroundColor?: string; // Default: white
  width?: number; // Force specific width
  height?: number; // Force specific height
}

/**
 * Convert a DOM element (containing chart) to base64 image
 * @param element - DOM element to convert (should contain the chart)
 * @param options - Export options
 * @returns Promise resolving to base64 image string
 */
export async function chartToImage(
  element: HTMLElement,
  options: ChartExportOptions = {}
): Promise<string> {
  const { scale = 2, backgroundColor = "#ffffff" } = options;

  try {
    // Add extra padding to capture axis labels and legends that might overflow
    const padding = 20; // pixels of extra space on all sides
    const captureWidth = element.offsetWidth + padding * 2;
    const captureHeight = element.offsetHeight + padding * 2;

    const dataUrl = await domtoimage.toPng(element, {
      bgcolor: backgroundColor,
      width: captureWidth * scale,
      height: captureHeight * scale,
      style: {
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        width: `${captureWidth}px`,
        height: `${captureHeight}px`,
        padding: `${padding}px`,
        boxSizing: "border-box",
      },
    });

    return dataUrl;
  } catch (error) {
    console.error("Error converting chart to image:", error);
    throw new Error("Failed to convert chart to image");
  }
}

/**
 * Convert multiple charts to images in parallel
 * @param elements - Array of chart elements with IDs
 * @returns Promise resolving to object with chart IDs as keys and base64 images as values
 */
export async function chartsToImages(
  elements: Array<{ id: string; element: HTMLElement }>,
  options: ChartExportOptions = {}
): Promise<Record<string, string>> {
  try {
    const promises = elements.map(async ({ id, element }) => {
      const image = await chartToImage(element, options);
      return { id, image };
    });

    const results = await Promise.all(promises);

    return results.reduce((acc, { id, image }) => {
      acc[id] = image;
      return acc;
    }, {} as Record<string, string>);
  } catch (error) {
    console.error("Error converting charts to images:", error);
    throw new Error("Failed to convert charts to images");
  }
}

/**
 * Helper to get chart element by data-chart-id attribute
 */
export function getChartElement(chartId: string): HTMLElement | null {
  return document.querySelector(`[data-chart-id="${chartId}"]`);
}

/**
 * Wait for chart to be fully rendered before capturing
 */
export async function waitForChartRender(delay: number = 500): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, delay));
}
