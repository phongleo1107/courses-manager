# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  # Frontend

  The frontend is a Vite + React + TypeScript starter. It currently displays the Vite demo; the course
  catalog, registration views, and Supabase Auth integration have not been implemented.

  ## Development

  From the repository root:

  ```bash
  npm --prefix frontend install
  npm --prefix frontend run dev
  ```

  The project also provides `npm --prefix frontend run build` and `npm --prefix frontend run lint`.
  There is no test runner configured yet.

  See [`../docs/frontend-setup.md`](../docs/frontend-setup.md) for the planned integration steps and
  [`../architecture.md`](../architecture.md) for the target frontend structure.
      },
