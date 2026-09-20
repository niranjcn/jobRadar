import Image from "next/image";

export function RadarMark({ size = 24 }: { size?: number }) {
  return (
    <Image
      src="/logo.png"
      alt="JobQuest"
      width={size}
      height={size}
      style={{ borderRadius: "50%" }}
    />
  );
}
