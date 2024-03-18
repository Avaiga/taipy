import { Color, Move, PieceSymbol } from "chess.js";
import { ChessPieceProps } from "./ChessPiece/ChessPiece";

export const getBoardFromFen = (fen: string): ChessPieceProps[] => {
  let pieces: ChessPieceProps[] = [];
  fen.split("/").forEach((row, index) => {
    if (index > 7) {
      return pieces;
    } else {
      let column = 1;
      row.split("").forEach((char) => {
        if (column <= 8) {
          if (isNaN(parseInt(char))) {
            let piece = char.toLowerCase() as PieceSymbol;
            let color: Color = char === char.toUpperCase() ? "w" : "b";
            pieces.push({
              position: [column, index + 1],
              piece,
              color,
            });
            column++;
          } else {
            column += parseInt(char);
          }
        }
      });
    }
  });
  return pieces;
};

export const getBoardFromMove = (move: Move): ChessPieceProps[] => {
  let pieces: ChessPieceProps[] = [];
  let lastChar = move.san.at(-1);
  let checkedData = [
    lastChar == "+" || lastChar == "#",
    move.piece,
    move.color,
  ];
  let board = getBoardFromFen(move.after);

  board.forEach(({ position, piece, color }) => {
    pieces.push({
      position,
      piece,
      color,
      checked: piece == "k" && checkedData[0] && checkedData[2] != color,
    });
  });
  return pieces;
};
