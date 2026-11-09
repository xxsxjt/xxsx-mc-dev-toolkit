package io.zershyan.examplemod.mixin.examplemod.client;

import io.zershyan.examplemod.client.ClientState;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Minecraft.class)
public class MixinMinecraft {
    @Inject(method = "setLevel", at = @At("HEAD"))
    private void examplemod$resetState(ClientLevel level, CallbackInfo ci) {
        ClientState.setValue(0);
    }
}
