export const darkThemeTemplate = {
    data: {
        barpolar: [
            {
                marker: {
                    line: {
                        color: "rgb(17,17,17)",
                    },
                    pattern: {
                        solidity: 0.2,
                    },
                },
                type: "barpolar",
            },
        ],
        bar: [
            {
                error_x: {
                    color: "#f2f5fa",
                },
                error_y: {
                    color: "#f2f5fa",
                },
                marker: {
                    line: {
                        color: "rgb(17,17,17)",
                    },
                    pattern: {
                        solidity: 0.2,
                    },
                },
                type: "bar",
            },
        ],
        carpet: [
            {
                aaxis: {
                    endlinecolor: "#A2B1C6",
                    gridcolor: "#506784",
                    linecolor: "#506784",
                    minorgridcolor: "#506784",
                    startlinecolor: "#A2B1C6",
                },
                baxis: {
                    endlinecolor: "#A2B1C6",
                    gridcolor: "#506784",
                    linecolor: "#506784",
                    minorgridcolor: "#506784",
                    startlinecolor: "#A2B1C6",
                },
                type: "carpet",
            },
        ],
        contour: [
            {
                colorscale: [
                    [0.0, "#0d0887"],
                    [0.1111111111111111, "#46039f"],
                    [0.2222222222222222, "#7201a8"],
                    [0.3333333333333333, "#9c179e"],
                    [0.4444444444444444, "#bd3786"],
                    [0.5555555555555556, "#d8576b"],
                    [0.6666666666666666, "#ed7953"],
                    [0.7777777777777778, "#fb9f3a"],
                    [0.8888888888888888, "#fdca26"],
                    [1.0, "#f0f921"],
                ],
                type: "contour",
            },
        ],
        heatmapgl: [
            {
                colorscale: [
                    [0.0, "#0d0887"],
                    [0.1111111111111111, "#46039f"],
                    [0.2222222222222222, "#7201a8"],
                    [0.3333333333333333, "#9c179e"],
                    [0.4444444444444444, "#bd3786"],
                    [0.5555555555555556, "#d8576b"],
                    [0.6666666666666666, "#ed7953"],
                    [0.7777777777777778, "#fb9f3a"],
                    [0.8888888888888888, "#fdca26"],
                    [1.0, "#f0f921"],
                ],
                type: "heatmapgl",
            },
        ],
        heatmap: [
            {
                colorscale: [
                    [0.0, "#0d0887"],
                    [0.1111111111111111, "#46039f"],
                    [0.2222222222222222, "#7201a8"],
                    [0.3333333333333333, "#9c179e"],
                    [0.4444444444444444, "#bd3786"],
                    [0.5555555555555556, "#d8576b"],
                    [0.6666666666666666, "#ed7953"],
                    [0.7777777777777778, "#fb9f3a"],
                    [0.8888888888888888, "#fdca26"],
                    [1.0, "#f0f921"],
                ],
                type: "heatmap",
            },
        ],
        histogram2dcontour: [
            {
                colorscale: [
                    [0.0, "#0d0887"],
                    [0.1111111111111111, "#46039f"],
                    [0.2222222222222222, "#7201a8"],
                    [0.3333333333333333, "#9c179e"],
                    [0.4444444444444444, "#bd3786"],
                    [0.5555555555555556, "#d8576b"],
                    [0.6666666666666666, "#ed7953"],
                    [0.7777777777777778, "#fb9f3a"],
                    [0.8888888888888888, "#fdca26"],
                    [1.0, "#f0f921"],
                ],
                type: "histogram2dcontour",
            },
        ],
        histogram2d: [
            {
                colorscale: [
                    [0.0, "#0d0887"],
                    [0.1111111111111111, "#46039f"],
                    [0.2222222222222222, "#7201a8"],
                    [0.3333333333333333, "#9c179e"],
                    [0.4444444444444444, "#bd3786"],
                    [0.5555555555555556, "#d8576b"],
                    [0.6666666666666666, "#ed7953"],
                    [0.7777777777777778, "#fb9f3a"],
                    [0.8888888888888888, "#fdca26"],
                    [1.0, "#f0f921"],
                ],
                type: "histogram2d",
            },
        ],
        histogram: [
            {
                marker: {
                    pattern: {
                        solidity: 0.2,
                    },
                },
                type: "histogram",
            },
        ],
        scatter: [
            {
                marker: {
                    line: {
                        color: "#283442",
                    },
                },
                type: "scatter",
            },
        ],
        scattergl: [
            {
                marker: {
                    line: {
                        color: "#283442",
                    },
                },
                type: "scattergl",
            },
        ],
        surface: [
            {
                colorscale: [
                    [0.0, "#0d0887"],
                    [0.1111111111111111, "#46039f"],
                    [0.2222222222222222, "#7201a8"],
                    [0.3333333333333333, "#9c179e"],
                    [0.4444444444444444, "#bd3786"],
                    [0.5555555555555556, "#d8576b"],
                    [0.6666666666666666, "#ed7953"],
                    [0.7777777777777778, "#fb9f3a"],
                    [0.8888888888888888, "#fdca26"],
                    [1.0, "#f0f921"],
                ],
                type: "surface",
            },
        ],
        table: [
            {
                cells: {
                    fill: {
                        color: "#506784",
                    },
                    line: {
                        color: "rgb(17,17,17)",
                    },
                },
                header: {
                    fill: {
                        color: "#2a3f5f",
                    },
                    line: {
                        color: "rgb(17,17,17)",
                    },
                },
                type: "table",
            },
        ],
    },
    layout: {
        annotationdefaults: {
            arrowcolor: "#f2f5fa",
        },
        colorscale: {
            diverging: [
                [0, "#8e0152"],
                [0.1, "#c51b7d"],
                [0.2, "#de77ae"],
                [0.3, "#f1b6da"],
                [0.4, "#fde0ef"],
                [0.5, "#f7f7f7"],
                [0.6, "#e6f5d0"],
                [0.7, "#b8e186"],
                [0.8, "#7fbc41"],
                [0.9, "#4d9221"],
                [1, "#276419"],
            ],
            sequential: [
                [0.0, "#0d0887"],
                [0.1111111111111111, "#46039f"],
                [0.2222222222222222, "#7201a8"],
                [0.3333333333333333, "#9c179e"],
                [0.4444444444444444, "#bd3786"],
                [0.5555555555555556, "#d8576b"],
                [0.6666666666666666, "#ed7953"],
                [0.7777777777777778, "#fb9f3a"],
                [0.8888888888888888, "#fdca26"],
                [1.0, "#f0f921"],
            ],
            sequentialminus: [
                [0.0, "#0d0887"],
                [0.1111111111111111, "#46039f"],
                [0.2222222222222222, "#7201a8"],
                [0.3333333333333333, "#9c179e"],
                [0.4444444444444444, "#bd3786"],
                [0.5555555555555556, "#d8576b"],
                [0.6666666666666666, "#ed7953"],
                [0.7777777777777778, "#fb9f3a"],
                [0.8888888888888888, "#fdca26"],
                [1.0, "#f0f921"],
            ],
        },
        colorway: [
            "#636efa",
            "#EF553B",
            "#00cc96",
            "#ab63fa",
            "#FFA15A",
            "#19d3f3",
            "#FF6692",
            "#B6E880",
            "#FF97FF",
            "#FECB52",
        ],
        font: {
            color: "#f2f5fa",
        },
        geo: {
            bgcolor: "rgb(17,17,17)",
            lakecolor: "rgb(17,17,17)",
            landcolor: "rgb(17,17,17)",
            subunitcolor: "#506784",
        },
        mapbox: {
            style: "dark",
        },
        map: {
            style: "dark",
        },
        paper_bgcolor: "rgb(17,17,17)",
        plot_bgcolor: "rgb(17,17,17)",
        polar: {
            angularaxis: {
                gridcolor: "#506784",
                linecolor: "#506784",
            },
            bgcolor: "rgb(17,17,17)",
            radialaxis: {
                gridcolor: "#506784",
                linecolor: "#506784",
            },
        },
        scene: {
            xaxis: {
                backgroundcolor: "rgb(17,17,17)",
                gridcolor: "#506784",
                linecolor: "#506784",
                zerolinecolor: "#C8D4E3",
            },
            yaxis: {
                backgroundcolor: "rgb(17,17,17)",
                gridcolor: "#506784",
                linecolor: "#506784",
                zerolinecolor: "#C8D4E3",
            },
            zaxis: {
                backgroundcolor: "rgb(17,17,17)",
                gridcolor: "#506784",
                linecolor: "#506784",
                showbackground: true,
                zerolinecolor: "#C8D4E3",
            },
        },
        shapedefaults: {
            line: {
                color: "#f2f5fa",
            },
        },
        sliderdefaults: {
            bgcolor: "#C8D4E3",
            bordercolor: "rgb(17,17,17)",
        },
        ternary: {
            aaxis: {
                gridcolor: "#506784",
                linecolor: "#506784",
            },
            baxis: {
                gridcolor: "#506784",
                linecolor: "#506784",
            },
            bgcolor: "rgb(17,17,17)",
            caxis: {
                gridcolor: "#506784",
                linecolor: "#506784",
            },
        },
        updatemenudefaults: {
            bgcolor: "#506784",
        },
        xaxis: {
            gridcolor: "#283442",
            linecolor: "#506784",
            tickcolor: "#506784",
            zerolinecolor: "#283442",
        },
        yaxis: {
            gridcolor: "#283442",
            linecolor: "#506784",
            tickcolor: "#506784",
            zerolinecolor: "#283442",
        },
    },
};
