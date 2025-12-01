import { useState } from "react";
import { Error as ErrorComponent } from "@/components/Error/error";

export const About = () => {
  const [error, setError] = useState<Error | null>(Error);

  if (error) {
    return <ErrorComponent />;
  }

  return (
    <div>
      <h1>About</h1>
      <p>This is the About page of the application.</p>
    </div>
  );
};
