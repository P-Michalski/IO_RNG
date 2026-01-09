import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  Download,
  FileText,
  Loader2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { toast } from "sonner";
import db_avatar from "@/assets/creators/db_avatar.jpg";
import mk_avatar from "@/assets/creators/mk_avatar.jpg";
import pm_avatar from "@/assets/creators/pm_avatar.jpg";
import documentationFile from "@/assets/IO_RNG.pdf?url";
import githubMark from "@/assets/github/github-mark.png";
import { useTheme } from "../theme-provider";
import { useSidebar } from "../ui/sidebar";

interface Creator {
  id: number;
  name: string;
  avatar: string;
  role: string;
  responsibility: string;
  github: string;
  githubUrl: string;
}

const creators: Creator[] = [
  {
    id: 1,
    name: "Dominik Bienia",
    avatar: db_avatar,
    role: "Student",
    responsibility: "Backend Developer",
    github: "@domelexe",
    githubUrl: "https://github.com/domelexe",
  },
  {
    id: 2,
    name: "Piotr Michalski",
    avatar: pm_avatar,
    role: "Student",
    responsibility: "Frontend Developer",
    github: "@P-Michalski",
    githubUrl: "https://github.com/P-Michalski",
  },
  {
    id: 3,
    name: "Mateusz Kania",
    avatar: mk_avatar,
    role: "Student",
    responsibility: "Algorithms Implementation",
    github: "@KaniaMateuszIT",
    githubUrl: "https://github.com/KaniaMateuszIT",
  },
];

export const About = () => {
  const [activeIndex, setActiveIndex] = useState(1);
  const [isHovered, setIsHovered] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [fileSize, setFileSize] = useState<string>("0 KB");
  const [isExpanded, setIsExpanded] = useState(false);
  const { theme } = useTheme();
  const { open } = useSidebar();

  useEffect(() => {
    if (isHovered) return;

    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % creators.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [isHovered]);

  useEffect(() => {
    const fetchFileSize = async () => {
      try {
        const response = await fetch(documentationFile, { method: "HEAD" });
        const contentLength = response.headers.get("content-length");

        if (contentLength) {
          const bytes = parseInt(contentLength, 10);
          const kb = bytes / 1024;
          const mb = kb / 1024;

          if (mb >= 1) {
            setFileSize(`${mb.toFixed(1)} MB`);
          } else {
            setFileSize(`${kb.toFixed(1)} KB`);
          }
        }
      } catch (error) {
        console.error("Failed to fetch file size:", error);
      }
    };

    fetchFileSize();
  }, []);

  const handleDownload = () => {
    setIsDownloading(true);
    try {
      const link = document.createElement("a");
      link.href = documentationFile;
      link.download = "IO_RNG.pdf";
      link.click();

      toast.success("Documentation downloaded successfully");
    } catch (error) {
      toast.error("Failed to download documentation");
    } finally {
      setIsDownloading(false);
    }
  };

  const getCardPosition = (index: number) => {
    const diff = (index - activeIndex + creators.length) % creators.length;

    if (diff === 0) {
      return "center";
    } else if (diff === 1 || diff === -2) {
      return "right";
    } else {
      return "left";
    }
  };

  return (
    <div className="container mx-auto p-8 max-w-6xl space-y-8">
      {/* Header */}
      <div className="space-y-2 text-center">
        <h1 className="text-4xl font-bold tracking-tight">About IO_RNG</h1>
        <p className="text-muted-foreground text-lg">
          Random Number Generator Testing & Analysis Platform
        </p>
      </div>

      {/* Project Description */}
      <Card>
        <CardHeader>
          <CardTitle>Project Overview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground leading-relaxed">
            IO_RNG is a comprehensive platform for testing and analyzing
            pseudorandom number generators (PRNGs). The project implements{" "}
            <strong>11 different algorithms</strong> including classical
            generators (LCG, Park-Miller, AWCG), modern fast PRNGs (PCG32,
            SplitMix64, Xorshift, Xoshiro256**), cryptographically secure
            generators (Blum Blum Shub, ChaCha20), and system RNGs (Python's
            built-in, OS RNG).
          </p>

          <div
            className={`grid transition-all duration-500 ease-in-out ${
              isExpanded
                ? "grid-rows-[1fr] opacity-100"
                : "grid-rows-[0fr] opacity-0"
            }`}
          >
            <div className="overflow-hidden">
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2 text-foreground">
                    Statistical Testing Suite
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    The platform provides extensive testing capabilities with{" "}
                    <strong>15 NIST Test Suite tests</strong> (including
                    Monobit, Runs, Matrix Rank, FFT, Overlapping/Non-Overlapping
                    Templates, Universal Statistical, Linear Complexity, Serial,
                    Approximate Entropy, Cumulative Sums, and Random
                    Excursions), <strong>5 Diehard Battery tests</strong>{" "}
                    (Birthday Spacings, Overlapping Permutations, Binary Rank,
                    Bitstream, OPSO), and{" "}
                    <strong>2 basic statistical tests</strong> (Chi-square
                    Frequency Test, Uniformity Test).
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-2 text-foreground">
                    Advanced Features
                  </h3>
                  <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                    <li>
                      <strong>Interactive Dashboard</strong> - Real-time
                      visualization of test results with comprehensive charts
                      and analytics
                    </li>
                    <li>
                      <strong>Batch Testing</strong> - Run multiple tests
                      simultaneously with different sample sizes and parameters
                    </li>
                    <li>
                      <strong>PDF Report Generation</strong> - Export detailed
                      reports with charts and statistical analysis
                    </li>
                    <li>
                      <strong>Custom Bit Testing</strong> - Test your own bit
                      sequences without saving to database
                    </li>
                    <li>
                      <strong>Bit Compression</strong> - Efficient storage with
                      94% space reduction using base64 encoding
                    </li>
                    <li>
                      <strong>Cross-Platform Support</strong> - Python, Rust,
                      and C# generators with unified interface
                    </li>
                    <li>
                      <strong>Parametric Generators</strong> - Customize LCG and
                      AWCG with your own parameters (multiplier, increment,
                      modulus)
                    </li>
                    <li>
                      <strong>Comprehensive Wiki</strong> - Detailed
                      documentation for all 11 implemented algorithms and 22
                      statistical tests, available in both Polish and English
                    </li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold mb-2 text-foreground">
                    Technical Implementation
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Built with modern technologies:{" "}
                    <strong>Django REST Framework</strong> for the backend with
                    Clean Architecture principles,{" "}
                    <strong>React + TypeScript</strong> for the frontend with
                    Tailwind CSS and shadcn/ui components,{" "}
                    <strong>SQLite</strong> database for efficient data storage,
                    and <strong>Recharts</strong> for interactive data
                    visualization. The project supports multiple programming
                    languages through a universal adapter pattern, enabling
                    seamless integration of Python modules, compiled executables
                    (Rust, C#), and system RNGs.
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-2 text-foreground">
                    Use Cases
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Perfect for researchers, students, and developers who need
                    to evaluate RNG quality for cryptographic applications,
                    statistical simulations, Monte Carlo methods, gaming
                    applications, or educational purposes. Compare different
                    algorithms, understand their statistical properties through
                    our extensive wiki, and make informed decisions about which
                    generator to use for your specific requirements.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full gap-2"
          >
            {isExpanded ? (
              <>
                View Less
                <ChevronUp className="h-4 w-4" />
              </>
            ) : (
              <>
                View More
                <ChevronDown className="h-4 w-4" />
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Documentation Download */}
      <Card>
        <CardHeader>
          <CardTitle>Documentation</CardTitle>
          <CardDescription>
            Download the complete project documentation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 border rounded-lg">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-primary/10 rounded-lg">
                <FileText className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="font-medium text-sm sm:text-base">IO_RNG.pdf</p>
                <p className="text-xs sm:text-sm text-muted-foreground">
                  {fileSize}
                </p>
              </div>
            </div>
            <Button
              onClick={handleDownload}
              disabled={isDownloading}
              className="gap-2 w-full sm:w-auto"
            >
              {isDownloading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Downloading...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4" />
                  Download
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Creators Carousel */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-center">Project Team</h2>
        <div
          className="relative h-[350px] sm:h-[400px] flex items-center justify-center px-4 sm:px-0 overflow-hidden"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          {creators.map((creator, index) => {
            const position = getCardPosition(index);
            const isActive = position === "center";

            return (
              <Card
                key={creator.id}
                className={`absolute transition-all duration-500 ease-in-out cursor-pointer hover:shadow-lg ${
                  position === "center"
                    ? "z-30 opacity-100 scale-100 lg:scale-105 xl:scale-110 w-[min(calc(100%-2rem),280px)] sm:w-[270px] md:w-[300px] lg:w-[320px] xl:w-[340px]"
                    : position === "left"
                    ? `z-10 ${
                        open
                          ? "opacity-0 md:opacity-0 xl:opacity-60"
                          : "opacity-0 sm:opacity-60"
                      } -translate-x-full sm:-translate-x-[170px] ${
                        open
                          ? "md:-translate-x-full xl:-translate-x-240px"
                          : "md:-translate-x-[200px] lg:-translate-x-240px"
                      } xl:-translate-x-[280px] scale-90 w-[min(calc(100%-3rem),240px)] sm:w-[230px] md:w-[260px] lg:w-[280px] xl:w-[300px]`
                    : `z-10 ${
                        open
                          ? "opacity-0 md:opacity-0 xl:opacity-60"
                          : "opacity-0 sm:opacity-60"
                      } translate-x-full sm:translate-x-[170px] ${
                        open
                          ? "md:translate-x-full xl:translate-x-240px"
                          : "md:translate-x-[200px] lg:translate-x-240px"
                      } xl:translate-x-[280px] scale-90 w-[min(calc(100%-3rem),240px)] sm:w-[230px] md:w-[260px] lg:w-[280px] xl:w-[300px]`
                }`}
                onClick={() => !isActive && setActiveIndex(index)}
              >
                <CardHeader className="text-center pb-4">
                  <div className="flex justify-center mb-4">
                    <Avatar className="h-20 w-20 sm:h-24 sm:w-24">
                      <AvatarImage src={creator.avatar} alt={creator.name} />
                      <AvatarFallback>
                        {creator.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  <CardTitle className="text-lg sm:text-xl">
                    {creator.name}
                  </CardTitle>
                  <CardDescription className="text-sm">
                    {creator.role}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <Badge
                      variant="secondary"
                      className="mb-2 text-xs sm:text-sm"
                    >
                      {creator.responsibility}
                    </Badge>
                  </div>
                  <Button
                    variant="outline"
                    className="w-full gap-2 text-sm"
                    asChild
                  >
                    <a
                      href={creator.githubUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Avatar
                        className={`h-4 w-4 ${
                          theme === "dark" ? "invert" : ""
                        }`}
                      >
                        <AvatarImage src={githubMark} alt="GitHub" />
                        <AvatarFallback>GH</AvatarFallback>
                      </Avatar>
                      {creator.github}
                    </a>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
        <div className="flex justify-center gap-2 mt-8">
          {creators.map((_, index) => (
            <button
              key={index}
              className={`h-2 rounded-full transition-all ${
                index === activeIndex
                  ? "w-8 bg-primary"
                  : "w-2 bg-muted-foreground/30 hover:bg-muted-foreground/50"
              }`}
              onClick={() => setActiveIndex(index)}
              aria-label={`Go to creator ${index + 1}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
