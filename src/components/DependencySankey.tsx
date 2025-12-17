"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts";

interface SankeyData {
  nodes: Array<{ name: string }>;
  links: Array<{ source: string; target: string; value: number }>;
}

interface DependencySankeyProps {
  data: SankeyData;
  title: string;
}

export default function DependencySankey({ data, title }: DependencySankeyProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstanceRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Initialize chart
    const chartInstance = echarts.init(chartRef.current);
    chartInstanceRef.current = chartInstance;

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: "item",
        triggerOn: "mousemove",
        backgroundColor: "rgba(0, 0, 0, 0.9)",
        borderColor: "#333",
        textStyle: {
          color: "#fff",
        },
      },
      series: [
        {
          type: "sankey",
          data: data.nodes,
          links: data.links,
          emphasis: {
            focus: "adjacency",
          },
          lineStyle: {
            color: "gradient",
            curveness: 0.5,
          },
          itemStyle: {
            borderWidth: 1,
            borderColor: "#000",
          },
          label: {
            color: "#fff",
            fontSize: 12,
            fontFamily: "monospace",
          },
          nodeGap: 12,
          layoutIterations: 32,
        },
      ],
    };

    chartInstance.setOption(option);

    // Handle window resize
    const handleResize = () => {
      chartInstance.resize();
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chartInstance.dispose();
    };
  }, [data]);

  return (
    <div className="bg-[#1a1a1a] rounded-lg p-6 border border-gray-800">
      <div
        ref={chartRef}
        className="w-full"
        style={{ height: "600px" }}
      />
      {data.nodes.length === 1 && (
        <p className="text-center text-gray-400 mt-4">
          No playbooks found in this track yet.
        </p>
      )}
    </div>
  );
}

