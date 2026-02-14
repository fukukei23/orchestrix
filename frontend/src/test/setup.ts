import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// テストごとにDOMをクリーンアップ
afterEach(() => {
  cleanup();
});

// テストマッチャーを拡張
expect.extend(matchers);
