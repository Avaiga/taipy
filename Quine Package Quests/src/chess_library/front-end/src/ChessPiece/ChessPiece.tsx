import { Color, PieceSymbol } from "chess.js";
import { King, Queen, Knight, Rook, Pawn, Bishop } from "../Icons";

import styles from "./ChessPiece.module.css";

export type ChessPieceProps = {
  position: [number, number];
  piece: PieceSymbol;
  color: Color;
  checked?: boolean;
};

const ChessPiece = ({
  position,
  piece,
  color,
  checked = false,
}: ChessPieceProps) => {
  const pieceMap = {
    k: King,
    q: Queen,
    n: Knight,
    r: Rook,
    p: Pawn,
    b: Bishop,
  };

  const Piece = pieceMap[piece];

  return (
    <div
      id={`piece-${position[0]}-${position[1]}`}
      style={{
        gridColumn: position[0],
        gridRow: position[1],
      }}
      className={checked ? styles.checked : styles.normal}
    >
      <Piece color={color} />
    </div>
  );
};

export default ChessPiece;
