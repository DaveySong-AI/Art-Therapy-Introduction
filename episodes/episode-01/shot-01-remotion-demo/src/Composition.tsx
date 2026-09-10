import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FPS = 30;
const DURATION_SECONDS = 14;

const clamp = (value: number) => Math.max(0, Math.min(1, value));
const draw = (frame: number, from: number, seconds: number) =>
  clamp((frame - from * FPS) / (seconds * FPS));

type StrokeProps = {
  d: string;
  frame: number;
  from: number;
  seconds: number;
  width?: number;
};

const Stroke: React.FC<StrokeProps> = ({d, frame, from, seconds, width = 5}) => {
  const progress = draw(frame, from, seconds);
  return (
    <path
      d={d}
      fill="none"
      pathLength={100}
      stroke="#1d1d1d"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={width}
      style={{strokeDasharray: 100, strokeDashoffset: 100 - progress * 100}}
    />
  );
};

const Marker: React.FC<{frame: number}> = ({frame}) => {
  const x = interpolate(frame, [0, 4 * FPS, 7 * FPS, 9 * FPS, 10.5 * FPS, 12 * FPS], [650, 705, 720, 760, 775, 775], {extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad)});
  const y = interpolate(frame, [0, 4 * FPS, 7 * FPS, 9 * FPS, 10.5 * FPS, 12 * FPS], [175, 260, 350, 515, 185, 185], {extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad)});
  return (
    <g opacity={frame < 12 * FPS ? 1 : 0} transform={`translate(${x} ${y}) rotate(-24)`}>
      <rect x="0" y="-8" width="115" height="25" rx="10" fill="#161616" />
      <rect x="84" y="-8" width="16" height="25" fill="#343434" />
      <path d="M-17 4 L0 -8 L0 17 Z" fill="#202020" />
      <circle cx="-12" cy="4" r="3" fill="#090909" />
    </g>
  );
};

export const Shot01Demo: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const completedOpacity = interpolate(frame, [11.5 * FPS, 12 * FPS], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic)});

  return (
    <AbsoluteFill style={{backgroundColor: "#fffefc"}}>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="100%">
        <g>
          <Stroke frame={frame} from={0} seconds={1.4} d="M570 250 C535 222 541 145 603 122 C676 93 754 138 746 211 C741 255 708 281 657 285" />
          <Stroke frame={frame} from={0.7} seconds={2.2} width={7} d="M556 175 C567 116 625 93 676 113 C711 108 741 134 750 171 M563 156 C592 116 622 126 640 144 M604 112 C611 148 629 160 639 172 M663 113 C658 151 676 165 691 177 M706 130 C693 161 718 178 726 193" />
          <Stroke frame={frame} from={2.1} seconds={1.7} d="M624 196 C634 187 649 188 655 202 M685 199 C696 190 708 193 713 206 M666 228 C676 235 688 235 697 228" width={4} />
          <Stroke frame={frame} from={3.6} seconds={2.1} d="M605 276 C575 298 555 337 562 405 M657 285 C682 302 707 321 721 363 M563 349 C596 367 640 373 683 359 M562 405 C611 417 672 418 726 407" />
          <Stroke frame={frame} from={5.4} seconds={1.7} d="M577 358 C595 404 615 432 656 440 C685 445 706 426 721 389 M597 355 C620 383 642 391 676 380" />
          <Stroke frame={frame} from={7} seconds={1.1} d="M255 443 C413 431 773 432 1010 439" width={5} />
          <Stroke frame={frame} from={8.1} seconds={1.4} d="M519 455 L718 455 L770 574 L467 574 Z" width={4} />
          <Stroke frame={frame} from={9.7} seconds={1.2} d="M735 106 C754 77 796 82 801 113 C805 143 776 149 763 130 M775 165 L775 169" width={5} />
        </g>
        <g opacity={completedOpacity}>
          <path d="M650 201 C663 210 676 210 688 201" fill="none" stroke="#1d1d1d" strokeWidth="4" strokeLinecap="round" />
          <circle cx="641" cy="201" r="5" fill="#1d1d1d" />
          <circle cx="703" cy="204" r="5" fill="#1d1d1d" />
        </g>
        <Marker frame={frame} />
      </svg>
    </AbsoluteFill>
  );
};

export const MyComposition: React.FC = () => (
  <Composition
    id="Shot01Demo"
    component={Shot01Demo}
    durationInFrames={DURATION_SECONDS * FPS}
    fps={FPS}
    width={1280}
    height={720}
  />
);
