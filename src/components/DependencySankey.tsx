"use client";

import { useEffect, useRef, useMemo } from "react";
import * as echarts from "echarts";

interface SankeyData {
  nodes: Array<{ name: string }>;
  links: Array<{ source: string; target: string; value: number }>;
}

interface DependencySankeyProps {
  data: SankeyData;
  title: string;
}

interface PreinstalledSoftware {
  type: string;
  name: string;
  linux: boolean;
  windows: boolean;
}

export default function DependencySankey({ data, title }: DependencySankeyProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstanceRef = useRef<echarts.ECharts | null>(null);

  // Transform data to consolidate platform-specific nodes (only leaf nodes)
  const consolidatedData = useMemo(() => {
    // Map to track leaf resources and their platforms
    const resourceMap = new Map<string, { baseName: string; platforms: Set<string> }>();
    const nodeMapping = new Map<string, string>(); // old node name -> new node name
    
    // First pass: identify which nodes are grouping nodes (have children)
    const groupingNodes = new Set<string>();
    data.links.forEach((link) => {
      groupingNodes.add(link.source);
    });
    
    // Second pass: identify leaf resources with platforms and group them
    data.nodes.forEach((node) => {
      const nodeName = node.name;
      const match = nodeName.match(/^(.+?)\s+\((LINUX|WINDOWS|ANY)\)$/);
      
      if (match) {
        const [, baseName, platform] = match;
        
        // Check if this is a grouping node (Apps, Frameworks, Models)
        const isGroupNode = baseName === "Apps" || baseName === "Frameworks" || baseName === "Models";
        
        // Only consolidate leaf nodes (non-grouping nodes)
        if (!isGroupNode && !groupingNodes.has(nodeName)) {
          const key = baseName;
          
          if (!resourceMap.has(key)) {
            resourceMap.set(key, {
              baseName,
              platforms: new Set(),
            });
          }
          
          resourceMap.get(key)!.platforms.add(platform);
        } else {
          // Keep grouping nodes and intermediate nodes as-is
          nodeMapping.set(nodeName, nodeName);
        }
      } else {
        // Non-platform nodes remain unchanged
        nodeMapping.set(nodeName, nodeName);
      }
    });
    
    // Create new consolidated node names for leaf resources only
    resourceMap.forEach(({ baseName, platforms }) => {
      const platformArray = Array.from(platforms).sort();
      let newNodeName: string;
      
      if (platformArray.length === 1) {
        newNodeName = `${baseName} (${platformArray[0]})`;
      } else {
        // Consolidate multiple platforms - format as uppercase with +
        const platformStr = platformArray.join('+');
        newNodeName = `${baseName} (${platformStr})`;
      }
      
      // Map all original node names to the new consolidated name
      platformArray.forEach(platform => {
        const oldNodeName = `${baseName} (${platform})`;
        nodeMapping.set(oldNodeName, newNodeName);
      });
    });
    
    // Create consolidated nodes (deduplicated)
    const consolidatedNodesSet = new Set(nodeMapping.values());
    const consolidatedNodes = Array.from(consolidatedNodesSet).map(name => ({ name }));
    
    // Transform links using the node mapping and aggregate values
    const linkMap = new Map<string, number>();
    
    data.links.forEach((link) => {
      const newSource = nodeMapping.get(link.source) || link.source;
      const newTarget = nodeMapping.get(link.target) || link.target;
      const linkKey = `${newSource}→${newTarget}`;
      
      linkMap.set(linkKey, (linkMap.get(linkKey) || 0) + link.value);
    });
    
    const consolidatedLinks = Array.from(linkMap.entries()).map(([key, value]) => {
      const [source, target] = key.split('→');
      return { source, target, value };
    });
    
    return {
      nodes: consolidatedNodes,
      links: consolidatedLinks,
    };
  }, [data]);

  // Extract preinstalled software from the Sankey data
  const preinstalledSoftware = useMemo(() => {
    const softwareMap = new Map<string, PreinstalledSoftware>();

    data.nodes.forEach((node) => {
      const nodeName = node.name;
      
      // Extract resource type and name from nodes like "Amuse (LINUX)" or "PyTorch (WINDOWS)"
      const match = nodeName.match(/^(.+?)\s+\((LINUX|WINDOWS|ANY)\)$/);
      
      if (match) {
        const [, resourceName, os] = match;
        
        // Skip grouping nodes (Apps, Frameworks, Models)
        if (resourceName === "Apps" || resourceName === "Frameworks" || resourceName === "Models") {
          return;
        }
        
        // Determine resource type based on parent nodes in the links
        let resourceType = "Unknown";
        
        // Find the parent link to determine type
        data.links.forEach((link) => {
          if (link.target === nodeName) {
            const parentName = link.source;
            if (parentName.includes("Apps")) resourceType = "App";
            else if (parentName.includes("Frameworks")) resourceType = "Framework";
            else if (parentName.includes("Models")) resourceType = "Model";
          }
        });
        
        const key = `${resourceType}:${resourceName}`;
        
        if (!softwareMap.has(key)) {
          softwareMap.set(key, {
            type: resourceType,
            name: resourceName,
            linux: false,
            windows: false,
          });
        }
        
        const software = softwareMap.get(key)!;
        if (os === "LINUX" || os === "ANY") software.linux = true;
        if (os === "WINDOWS" || os === "ANY") software.windows = true;
      }
    });

    // Combine vllm and docker into a single entry
    const vllmKey = "Framework:vllm";
    const dockerKey = "Framework:docker";
    
    if (softwareMap.has(vllmKey) && softwareMap.has(dockerKey)) {
      const vllm = softwareMap.get(vllmKey)!;
      const docker = softwareMap.get(dockerKey)!;
      
      // Create combined entry
      softwareMap.set(vllmKey, {
        type: vllm.type,
        name: "vllm (+docker)",
        linux: vllm.linux || docker.linux,
        windows: vllm.windows || docker.windows,
      });
      
      // Remove separate docker entry
      softwareMap.delete(dockerKey);
    } else if (softwareMap.has(vllmKey)) {
      // If vllm exists without docker, still rename it
      const vllm = softwareMap.get(vllmKey)!;
      softwareMap.set(vllmKey, {
        ...vllm,
        name: "vllm (+docker)",
      });
    }

    return Array.from(softwareMap.values()).sort((a, b) => {
      // Always put lemonade last
      if (a.name.toLowerCase().includes('lemonade')) return 1;
      if (b.name.toLowerCase().includes('lemonade')) return -1;
      
      // Sort by type first, then by name
      if (a.type !== b.type) return a.type.localeCompare(b.type);
      return a.name.localeCompare(b.name);
    });
  }, [data]);

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
          data: consolidatedData.nodes,
          links: consolidatedData.links,
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
  }, [consolidatedData]);

  return (
    <div className="bg-[#1a1a1a] rounded-lg p-6 border border-gray-800">
      <div
        ref={chartRef}
        className="w-full"
        style={{ height: "600px" }}
      />
      {consolidatedData.nodes.length === 1 && (
        <p className="text-center text-gray-400 mt-4">
          No playbooks found in this track yet.
        </p>
      )}

      {/* Preinstalled Software Table */}
      {preinstalledSoftware.length > 0 && (
        <div className="mt-8">
          <h3 className="text-xl font-semibold text-white mb-4">
            Preinstalled SW
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-300 font-semibold w-32">
                    Resource Type
                  </th>
                  <th className="text-left py-3 px-4 text-gray-300 font-semibold">
                    Resource Name
                  </th>
                  <th className="text-center py-3 px-4 text-gray-300 font-semibold w-24">
                    Linux
                  </th>
                  <th className="text-center py-3 px-4 text-gray-300 font-semibold w-24">
                    Windows
                  </th>
                </tr>
              </thead>
              <tbody>
                {(() => {
                  // Group software by type for rowspan rendering
                  const groupedByType: { [key: string]: PreinstalledSoftware[] } = {};
                  preinstalledSoftware.forEach((software) => {
                    if (!groupedByType[software.type]) {
                      groupedByType[software.type] = [];
                    }
                    groupedByType[software.type].push(software);
                  });

                  return Object.entries(groupedByType).map(([type, items]) => 
                    items.map((software, index) => (
                      <tr
                        key={`${software.type}-${software.name}-${index}`}
                        className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors"
                      >
                        {index === 0 && (
                          <td
                            className="py-3 px-4 text-gray-400 font-semibold border-r border-gray-700 align-top"
                            rowSpan={items.length}
                          >
                            {type}
                          </td>
                        )}
                        <td className="py-3 px-4 text-white font-mono">
                          {software.name}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {software.linux ? (
                            <span className="text-green-400 text-xl">✓</span>
                          ) : (
                            <span className="text-gray-600 text-xl">✗</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {software.windows ? (
                            <span className="text-green-400 text-xl">✓</span>
                          ) : (
                            <span className="text-gray-600 text-xl">✗</span>
                          )}
                        </td>
                      </tr>
                    ))
                  );
                })()}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

