package io.zershyan.examplemod.compat;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.loading.FMLEnvironment;
import net.minecraftforge.network.simple.SimpleChannel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.Callable;

public interface ICompatUtils {
    Logger LOGGER = LoggerFactory.getLogger(ICompatUtils.class);

    default boolean testLoadedAndRun(Runnable runnable) {
        if (!isModLoaded()) return false;
        runnable.run();
        return true;
    }

    default <T> T testLoadedAndCall(Callable<T> callable, T errorResult) {
        try {
            if (isModLoaded()) return callable.call();
        } catch (Exception ignored) {
        }
        return errorResult;
    }

    default <T> T testLoadedAndCall(Callable<T> callable, Callable<T> elseCall, T errorResult) {
        try {
            return isModLoaded() ? callable.call() : elseCall.call();
        } catch (Exception e) {
            return errorResult;
        }
    }

    default void addCommonListener(IEventBus forgeBus, IEventBus modBus) {
    }

    default void addClientListener(IEventBus forgeBus, IEventBus modBus) {
    }

    default void addListener(IEventBus forgeBus, IEventBus modBus) {
        addCommonListener(forgeBus, modBus);
        if (FMLEnvironment.dist == Dist.CLIENT) {
            addClientListener(forgeBus, modBus);
        }
    }

    default void init(IEventBus forgeBus, IEventBus modBus) {
        addListener(forgeBus, modBus);
    }

    default void initial(IEventBus forgeBus, IEventBus modBus) {
        try {
            testLoadedAndRun(() -> init(forgeBus, modBus));
        } catch (Exception e) {
            LOGGER.error("初始化兼容层失败", e);
        }
    }

    default void safelyRun(Runnable runnable) {
        try {
            runnable.run();
        } catch (Exception ignored) {
        }
    }

    default void initNetwork(SimpleChannel channel) {
        try {
            testLoadedAndRun(() -> registerNetwork(channel));
        } catch (Exception e) {
            LOGGER.error("注册兼容层网络包失败", e);
        }
    }

    default void registerNetwork(SimpleChannel channel) {
    }

    boolean isModLoaded();
}
