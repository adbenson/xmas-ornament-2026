const Pixel: FC<{id: number, x: number, y: number, state: PixelState}> = ({id, state}) => {
    return <div className={styles.pixel}>
        {id}
    </div>
}