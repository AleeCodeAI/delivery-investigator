/*
 * Logo: dossier with a magnifying lens, as in the approved mockups.
 * Use showName to render the logo together with the product name.
 */

interface LogoProps {
  size?: number
  showName?: boolean
}

export function Logo({ size = 26, showName = false }: LogoProps) {
  return (
    <div className="flex items-center gap-2.5">
      <svg width={size} height={size} viewBox="0 0 28 28" fill="none" aria-hidden="true">
        <path d="M5 4.5C5 3.67 5.67 3 6.5 3H15.5L20 7.5V11" stroke="#111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M5 4.5V22.5C5 23.33 5.67 24 6.5 24H12" stroke="#111" strokeWidth="2" strokeLinecap="round" />
        <path d="M8.5 9H13.5M8.5 13H11.5" stroke="#8A8A8F" strokeWidth="1.75" strokeLinecap="round" />
        <circle cx="17.5" cy="17.5" r="5.5" fill="#fff" stroke="#111" strokeWidth="2.35" />
        <path d="M21.5 21.5L25 25" stroke="#111" strokeWidth="2.6" strokeLinecap="round" />
      </svg>
      {showName && <span className="text-[15px] font-semibold tracking-[-0.01em]">Delivery Investigator</span>}
    </div>
  )
}