import { useDynamicProperty } from "taipy-gui";
import ChessPiece, { ChessPieceProps } from "../ChessPiece/ChessPiece";
import MoveList from "../MoveList/MoveList";
import { useEffect, useState } from "react";
import { Chess, Move, PieceSymbol, Color } from "chess.js";

import styles from "./ChessBoard.module.css";
import { getBoardFromFen, getBoardFromMove } from "../utils";

const chess = new Chess();

interface ChessBoardProps {
  data?: string;
  defaultData?: string;
}

const getVictoryMessage = (victoryStatus: string, winner: string) => {
  switch (victoryStatus) {
    case "mate":
      return winner == "white"
        ? "White wins by checkmate"
        : "Black wins by checkmate";
    case "resign":
      return winner == "white"
        ? "White wins by resignation"
        : "Black wins by resignation";
    case "outoftime":
      return winner == "draw"
        ? "Draw, insufficient resources"
        : winner == "white"
        ? "White wins on time"
        : "Black wins on time";
    case "draw":
      return "Draw";
    default:
      return "In progress";
  }
};

type ChessData = {
  moves: string;
  whiteId: string;
  blackId: string;
  whiteRating: number;
  blackRating: number;
  victoryStatus: string;
  openingName: string;
  winner: string;
};

const ChessBoard = (props: ChessBoardProps) => {
  const data = useDynamicProperty(props.data, props.defaultData, "");
  const [chessData, setChessData] = useState<ChessData>({
    moves: "",
    whiteId: "",
    blackId: "",
    whiteRating: 0,
    blackRating: 0,
    victoryStatus: "",
    openingName: "",
    winner: "",
  });
  const [index, setIndex] = useState(-1);
  const [history, setHistory] = useState<Move[]>([]);

  useEffect(() => {
    if (data) {
      let splitData = data.split("/");
      setChessData({
        moves: splitData[0],
        whiteId: splitData[1],
        blackId: splitData[2],
        whiteRating: parseInt(splitData[3]),
        blackRating: parseInt(splitData[4]),
        victoryStatus: splitData[5],
        winner: splitData[6],
        openingName: splitData[7],
      });
    }
  }, [data]);

  useEffect(() => {
    let history: Move[] = [];
    chess.load("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    setIndex(-1);
    if (chessData.moves) {
      chessData.moves.split(" ").forEach((move) => {
        history.push(chess.move(move));
      });
    }
    console.log(history);
    setHistory(history);
  }, [chessData]);

  if (chessData.moves === "") {
    return <div />;
  }

  return (
    <div className={styles.panel}>
      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.opening_name}>{chessData.openingName}</div>
          {chessData.whiteId.length > 0 && chessData.blackId.length > 0 && (
            <>
              <div className={styles.players}>
                <div className={styles.players}>
                  <div className={styles.player}>
                    <div>{chessData.whiteId} </div>
                    <div>(white)</div>
                    <div className={styles.rating}>{chessData.whiteRating}</div>
                  </div>
                  <div className={styles.player}>
                    <div>{chessData.blackId} </div>
                    <div>(black)</div>
                    <div className={styles.rating}>{chessData.blackRating}</div>
                  </div>
                </div>
              </div>
              {index == history.length - 1 ? (
                <div className={styles.victory_status}>
                  {getVictoryMessage(chessData.victoryStatus, chessData.winner)}
                </div>
              ) : (
                <div>
                  <div className={styles.victory_status}>In progress</div>
                </div>
              )}
            </>
          )}
        </div>
        <div className={styles.board}>
          <div className={styles.grid}>
            {Array.from({ length: 8 }, (_, i) => i + 1).map((i) =>
              Array.from({ length: 8 }, (_, j) => j + 1).map((j) => (
                <div
                  key={`${i}-${j}`}
                  style={{
                    gridColumn: i,
                    gridRow: j,
                    backgroundColor:
                      (i + j) % 2 === 0
                        ? "rgba(240,217,181,255)"
                        : "rgba(181,136,99,255)",
                  }}
                />
              ))
            )}

            {index === -1 || index > history.length - 1
              ? getBoardFromFen(
                  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
                ).map((piece) => (
                  <ChessPiece
                    position={piece.position}
                    piece={piece.piece}
                    color={piece.color}
                  />
                ))
              : getBoardFromMove(history[index]).map((piece) => (
                  <ChessPiece
                    position={piece.position}
                    piece={piece.piece}
                    color={piece.color}
                    checked={piece.checked}
                  />
                ))}
          </div>
          <MoveList index={index} moves={chessData.moves} setIndex={setIndex} />
        </div>
        <div className={styles.control_buttons}>
          <button
            className={styles.control_button}
            onClick={() => {
              if (index > 0) {
                setIndex(index - 1);
              }
            }}
          >
            {"<"}
          </button>
          <button
            className={styles.control_button}
            onClick={() => {
              if (index < history.length - 1) {
                setIndex(index + 1);
              }
            }}
          >
            {">"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChessBoard;
