
from typing import Type, Dict, Callable, Any, Optional, Tuple
import inspect
import asyncio

class IoCContainer:
    """轻量版 IoC 容器（支持异步 shutdown，兼容同步/异步析构函数）"""

    _instance: Optional["IoCContainer"] = None  # 单例引用

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._providers: Dict[str, Tuple[Callable[[], Any], bool]] = {}
        self._instances: Dict[str, Any] = {}
        self._destructors: Dict[str, Callable[[Any], Any]] = {}
        self._shutdown_flag = False
        self._initialized = True

    # ---------- 静态获取 ----------
    @classmethod
    def get_instance(cls) -> "IoCContainer":
        return cls()

    # ---------- 注册 ----------
    def register_class(
        self,
        key: str,
        cls: Type,
        singleton: bool = True,
        constructor_args: Optional[tuple] = None,
        constructor_kwargs: Optional[dict] = None,
        destructor: Optional[Callable[[Any], Any]] = None,
        allow_override: bool = False,
    ):
        constructor_args = constructor_args or ()
        constructor_kwargs = constructor_kwargs or {}
        provider = lambda: cls(*constructor_args, **constructor_kwargs)
        self.register_provider(key, provider, singleton, destructor, allow_override)

    def register_provider(
        self,
        key: str,
        provider: Callable[[], Any],
        singleton: bool = True,
        destructor: Optional[Callable[[Any], Any]] = None,
        allow_override: bool = False,
    ):
        if key in self._providers and not allow_override:
            raise KeyError(f"❌ Provider for '{key}' already exists (use allow_override=True to replace).")
        if key in self._providers:
            self._destroy_instance(key)
        self._providers[key] = (provider, singleton)
        if destructor:
            self._destructors[key] = destructor

    def register_instance(
        self,
        key: str,
        instance: Any,
        destructor: Optional[Callable[[Any], Any]] = None,
        allow_override: bool = False,
    ):
        if key in self._providers and not allow_override:
            raise KeyError(f"❌ Instance for '{key}' already exists (use allow_override=True to replace).")
        if key in self._providers:
            self._destroy_instance(key)

        self._instances[key] = instance
        self._providers[key] = (lambda: instance, True)  # 始终单例
        self._destructors[key] = destructor or self._auto_destructor(instance)

    # ---------- 解析 ----------
    def resolve(self, key: str) -> Any:
        if self._shutdown_flag:
            raise RuntimeError("❌ IoCContainer has been shut down — cannot resolve further.")
        if key not in self._providers:
            raise ValueError(f"❌ Provider for '{key}' not found.")

        provider, singleton = self._providers[key]
        if singleton and key in self._instances:
            return self._instances[key]

        instance = provider()
        if singleton:
            self._instances[key] = instance
            if key not in self._destructors:
                self._destructors[key] = self._auto_destructor(instance)
        return instance

    # ---------- 自动析构探测 ----------
    def _auto_destructor(self, instance: Any) -> Optional[Callable[[Any], Any]]:
        """
        自动探测实例中的 close/shutdown/dispose 方法，返回原始引用，支持 async def。
        """
        for method_name in ("close", "shutdown", "dispose"):
            method = getattr(instance, method_name, None)
            if method and callable(method):
                return method
        return None

    # ---------- 删除实例 ----------
    async def _destroy_instance(self, key: str):
        instance = self._instances.pop(key, None)
        destructor = self._destructors.pop(key, None)
        self._providers.pop(key, None)  # 可选：注释以保留 provider

        if instance and destructor:
            try:
                result = destructor()
                if inspect.isawaitable(result):
                    await result
                print(f"[IoC] ✅ Destroyed: {key}")
            except Exception as e:
                print(f"[IoC] ❌ Failed to destroy {key}: {e}")

    # ---------- 主动初始化所有 singleton ----------
    def initialize_all_singletons(self):
        for key, (provider, singleton) in self._providers.items():
            if singleton and key not in self._instances:
                try:
                    instance = provider()
                    self._instances[key] = instance
                    if key not in self._destructors:
                        self._destructors[key] = self._auto_destructor(instance)
                    print(f"[IoC] ✅ Initialized: {key}")
                except Exception as e:
                    print(f"[IoC] ❌ Failed to initialize '{key}': {e}")

    # ---------- 异步关闭 ----------
    async def shutdown(self):
        if self._shutdown_flag:
            return
        self._shutdown_flag = True
        print("🔻 IoCContainer shutting down...")
        for key in list(self._instances.keys()):
            await self._destroy_instance(key)


