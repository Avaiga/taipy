import { useEffect, useState } from "react";

import styles from "./MoveList.module.css";

interface MoveProps {
  index: number;
  move: string;
  setIndex: (index: number) => void;
  selected: boolean;
}

const Move = ({ index, move, setIndex, selected }: MoveProps) => {
  return (
    <div
      key={`move-${index}`}
      onClick={() => {
        setIndex(index);
      }}
      className={selected ? styles.selected : styles.move}
    >
      {move}
    </div>
  );
};

interface MoveListProps {
  moves: String;
  index: number;
  setIndex: (index: number) => void;
}

const MoveList = ({ index, moves, setIndex }: MoveListProps) => {
  const movesArray = moves.split(" ");

  return (
    <div className={styles.list}>
      {Array.from(
        {
          length:
            movesArray.length % 2 == 0
              ? movesArray.length / 2
              : movesArray.length / 2 + 1,
        },
        (_, i) => i
      ).map((i) => {
        return (
          <div
            style={{
              display: "flex",
              gap: "10px",
              width: "100%",
              height: "30px",
              backgroundColor:
                i % 2 === 0 ? "rgba(0,0,0,0.0)" : "rgba(0,0,0,0.2)",
            }}
          >
            <div
              style={{
                textAlign: "right",
                width: "20px",
              }}
            >
              {i + 1}.
            </div>
            <div
              style={{
                display: "flex",
              }}
            >
              <Move
                index={i * 2}
                move={movesArray[i * 2]}
                setIndex={setIndex}
                selected={index === i * 2}
              />
              {i * 2 + 1 < movesArray.length && (
                <Move
                  index={i * 2 + 1}
                  move={movesArray[i * 2 + 1]}
                  setIndex={setIndex}
                  selected={index === i * 2 + 1}
                />
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MoveList;
