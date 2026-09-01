import { useState, type FC, type JSX } from "react";
import { range } from "../util/utils";
import styles from "./PixelPalette.module.css";

type PixelState = 'on' | 'off';

const rows = 9;
const columns = 18;

export const PixelPalette: FC = () => {

    const [pixelState] = useState<PixelState[]>(() => range(rows * columns).map(() => 'off'));

    const [pixels] = useState<JSX.Element[][]>(() =>
        range(rows).map((x) => range(columns).map((y) => <Pixel key={x * columns + y} id={x * columns + y} x={x} y={y} state={pixelState[x * columns + y]} />)));

    return <div className={styles["pixel-palette"]}>
        {pixels.map((row, i) =>
            <div key={i} className={styles["pixel-row"]}>
                {row}
            </div>
            )}
    </div>
}

const Pixel: FC<{id: number, x: number, y: number, state: PixelState}> = ({id, state}) => {
    return <div className={styles.pixel}>
        {id}
    </div>
}