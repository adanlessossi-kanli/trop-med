import createMiddleware from "next-intl/middleware";
import { defineRouting } from "next-intl/routing";

const routing = defineRouting({
  locales: ["fr", "en"],
  defaultLocale: "fr",
});

export default createMiddleware(routing);

export const config = {
  matcher: ["/((?!_next|api|favicon.ico|health).*)"],
};
