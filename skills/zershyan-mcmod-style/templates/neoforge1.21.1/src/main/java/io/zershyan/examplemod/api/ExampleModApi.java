package io.zershyan.examplemod.api;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.world.level.Level;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;

/**
 * 本体 API，任意包可直接调用，本包也可调用内部逻辑。
 */
public class ExampleModApi {
    public static final String MODID = ExampleMod.MODID;

    /**
     * 获取部分 tick，客户端返回真实值，服务端返回 0。
     *
     * @param level 世界
     * @return 部分 tick
     */
    public static float tryGetPartialTick(Level level) {
        if (level.isClientSide()) {
            return clientGetPartialTick();
        } else return 0;
    }

    @OnlyIn(Dist.CLIENT)
    public static float clientGetPartialTick() {
        return net.minecraft.client.Minecraft.getInstance().getTimer().getGameTimeDeltaPartialTick(true);
    }
}
