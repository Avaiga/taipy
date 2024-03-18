import { useDynamicProperty } from "taipy-gui";
import styles from "./HeatMap.module.css";
import { useEffect, useState } from "react";
import ChessPiece, { ChessPieceProps } from "../ChessPiece/ChessPiece";
import { Color, PieceSymbol } from "chess.js";
import { getBoardFromFen } from "../utils";

const squares = [
  "a8",
  "b8",
  "c8",
  "d8",
  "e8",
  "f8",
  "g8",
  "h8",
  "a7",
  "b7",
  "c7",
  "d7",
  "e7",
  "f7",
  "g7",
  "h7",
  "a6",
  "b6",
  "c6",
  "d6",
  "e6",
  "f6",
  "g6",
  "h6",
  "a5",
  "b5",
  "c5",
  "d5",
  "e5",
  "f5",
  "g5",
  "h5",
  "a4",
  "b4",
  "c4",
  "d4",
  "e4",
  "f4",
  "g4",
  "h4",
  "a3",
  "b3",
  "c3",
  "d3",
  "e3",
  "f3",
  "g3",
  "h3",
  "a2",
  "b2",
  "c2",
  "d2",
  "e2",
  "f2",
  "g2",
  "h2",
  "a1",
  "b1",
  "c1",
  "d1",
  "e1",
  "f1",
  "g1",
  "h1",
];

const DegreeColors = [
  [255, 41, 87], // min
  [95, 23, 252], // mid
  [28, 255, 126], // end
];

const getIndexOfSquare = (square: string) => {
  return squares.indexOf(square);
};

const getPieceOnIndex = (index: number) => {
  return squares[index];
};

type PieceData = {
  color: Color;
  piece: PieceSymbol;
};

const getPieceOnSquare = (square: string): PieceData => {
  switch (square) {
    case "f3":
      return {
        color: "w",
        piece: "n",
      };
    case "c3":
      return {
        color: "w",
        piece: "n",
      };
    case "f6":
      return {
        color: "b",
        piece: "n",
      };
    case "c6":
      return {
        color: "b",
        piece: "n",
      };
    default:
      return {
        color: getIndexOfSquare(square) < 32 ? "b" : "w",
        piece: "p",
      };
  }
};

const getBracketFromDegree = (degree: number) => {
  if (degree <= 10 && degree > 0) return 0.1;
  if (degree <= 20 && degree > 10) return 0.2;
  if (degree <= 30 && degree > 20) return 0.3;
  if (degree <= 40 && degree > 30) return 0.4;
  if (degree <= 50 && degree > 40) return 0.5;
  if (degree <= 60 && degree > 50) return 0.6;
  if (degree <= 70 && degree > 60) return 0.7;
  if (degree <= 80 && degree > 70) return 0.8;
  if (degree <= 90 && degree > 80) return 0.9;
  if (degree <= 100 && degree > 90) return 1.0;
  return 0;
};

const getColor = (degree: number) => {
  const bracket = getBracketFromDegree(degree);
  if (bracket <= 0.5) {
    return `hsl(${280 - bracket * 2 * 80}, 100%, ${30 + bracket * 2 * 20}%)`;
  } else {
    return `hsl(${200 - (bracket * 2 - 1) * 200}, 100%, ${
      50 + (bracket * 2 - 1)
    }%)`;
  }
};

interface HeatmapBarProps {
  min: number;
  max: number;
}

const getThousands = (n: number): number => {
  if (n >= 100000) {
    return 10000;
  }
  if (n >= 10000) {
    return 1000;
  }
  return 100;
};

const HeatmapBar = ({ min, max }: HeatmapBarProps) => {
  let max_ceil = getThousands(max);
  return (
    <div style={{ position: "relative", height: "100%", marginLeft: "10px" }}>
      <div
        style={{
          width: "10px",
          height: "100%",
          background: `linear-gradient(to top, ${getColor(0)}, ${getColor(
            10
          )}, ${getColor(20)}, ${getColor(30)}, ${getColor(40)}, ${getColor(
            50
          )}, ${getColor(60)}, ${getColor(70)}, ${getColor(80)}, ${getColor(
            90
          )}, ${getColor(100)})`,
        }}
      />
      {Array.from({ length: 10 }).map((_, i) => {
        let value =
          Math.ceil(((max - min) * (i / 10) + min) / max_ceil) * max_ceil;
        return (
          <div
            key={i}
            style={{
              bottom: `${i * 10 - 3.5}%`,
            }}
            className={styles.heatmapBarText}
          >
            {`${max_ceil >= 1000 ? value / 1000 : value}${
              getThousands(max) > 100 && value != 0 ? "k" : ""
            }`}
          </div>
        );
      })}
    </div>
  );
};

interface HeatMapProps {
  data?: string;
  defaultData?: string;
}

const HeatMap = (props: HeatMapProps) => {
  const data = useDynamicProperty(props.data, props.defaultData, "");
  const [isFirstMoveData, setIsFirstMoveData] = useState(false);
  const [title, setTitle] = useState("");

  const [degrees, setDegrees] = useState<Array<number>>();
  const [max, setMax] = useState(0);
  const [min, setMin] = useState(0);

  useEffect(() => {
    if (data) {
      const numbers: number[] = [];

      data.split(",").forEach((n, index) => {
        if (index < 64) numbers.push(parseInt(n));
        else if (index == 64) setIsFirstMoveData(parseInt(n) == 1);
        else setTitle(n);
      });

      const max = Math.max(...numbers);
      const min = Math.min(...numbers);

      console.log(max);

      setDegrees(
        numbers.map((n) => {
          let percent = ((n - min) / (max - min)) * 100;
          return percent;
        })
      );

      setMax(max);
      setMin(min);
    }
  }, [data]);

  return (
    <div className={styles.panel}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>{title}</h1>
        </div>
        <div className={styles.board}>
          <div className={styles.grid}>
            {degrees?.map((degree, index) => {
              let square = getPieceOnIndex(index);

              return (
                <div
                  key={index}
                  style={{
                    gridColumn: (index % 8) + 1,
                    gridRow: Math.floor(index / 8) + 1,
                    backgroundColor: getColor(degree),
                    display: "flex",
                    border: "1px solid black",
                  }}
                >
                  {((isFirstMoveData && index >= 16 && index < 48) ||
                    !isFirstMoveData) && (
                    <div className={styles.square}>{square}</div>
                  )}
                </div>
              );
            })}

            {isFirstMoveData &&
              getBoardFromFen(
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
              ).map((piece) => (
                <ChessPiece
                  position={piece.position}
                  piece={piece.piece}
                  color={piece.color}
                />
              ))}
          </div>
          <HeatmapBar min={min} max={max} />
        </div>
      </div>
    </div>
  );
};

export default HeatMap;
