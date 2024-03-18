import { Color, PieceSymbol } from "chess.js";

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

export const getPieceOnSquare = (square: string): PieceData => {
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
export const getColorBasedOnDegree = (degree: number) => {
  if (degree === 0) {
    return `rgba(255, 255, 255, 0.5)`;
  }
  let color =
    degree < 50
      ? DegreeColors[0].map((c, index) => {
          return c + (DegreeColors[1][index] - c) * (degree / 50);
        })
      : DegreeColors[1].map((c, index) => {
          return c + (DegreeColors[2][index] - c) * ((degree - 50) / 50);
        });

  return `rgba(${color[0]},${color[1]},${color[2]},0.5)`;
};
