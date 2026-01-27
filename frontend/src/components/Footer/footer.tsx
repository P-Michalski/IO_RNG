export const Footer = () => {
  return (
    <footer className="border-t mt-auto">
      <div className="container mx-auto p-6">
        <p className="text-sm text-muted-foreground text-center">
          © {new Date().getFullYear()} IO_RNG Project. Licensed under the MIT
          License.
        </p>
      </div>
    </footer>
  );
};
