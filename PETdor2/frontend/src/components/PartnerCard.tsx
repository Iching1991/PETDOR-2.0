interface PartnerCardProps {
  name: string;
  logo: string;
  url: string;
}

const PartnerCard = ({ name, logo, url }: PartnerCardProps) => {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="wellness-card group cursor-pointer transform hover:scale-105 transition-smooth"
    >
      <div className="aspect-video flex items-center justify-center p-6 bg-gradient-to-br from-primary/5 to-secondary/5 rounded-xl">
        <img
          src={logo}
          alt={`${name} logo`}
          className="max-w-full max-h-full object-contain filter grayscale group-hover:grayscale-0 transition-smooth"
        />
      </div>
      <div className="mt-4 text-center">
        <h3 className="font-semibold text-foreground group-hover:text-primary transition-smooth">
          {name}
        </h3>
      </div>
    </a>
  );
};

export default PartnerCard;
