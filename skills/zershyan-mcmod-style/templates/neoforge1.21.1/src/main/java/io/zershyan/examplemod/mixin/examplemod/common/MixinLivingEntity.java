package io.zershyan.examplemod.mixin.examplemod.common;

import io.zershyan.examplemod.util.mixin.examplemod.common.IMixinLivingEntity;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;

@Mixin(LivingEntity.class)
public class MixinLivingEntity implements IMixinLivingEntity {
    @Unique
    private boolean examplemod$marked;

    @Override
    public boolean examplemod$isMarked() {
        return examplemod$marked;
    }

    @Override
    public void examplemod$setMarked(boolean marked) {
        this.examplemod$marked = marked;
    }
}
