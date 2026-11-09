package io.zershyan.examplemod.mixin;

import net.neoforged.fml.loading.LoadingModList;
import net.neoforged.fml.loading.moddiscovery.ModInfo;
import org.objectweb.asm.tree.ClassNode;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

import java.util.List;
import java.util.Set;

public class ExampleModMixinPlugin implements IMixinConfigPlugin {
    @Override
    public void onLoad(String mixinPackage) {

    }

    @Override
    public String getRefMapperConfig() {
        return "";
    }

    @Override
    public boolean shouldApplyMixin(String targetClassName, String mixinClassName) {
        if (mixinClassName.contains(".example.mixin.")) return false;
        List<String> modIds = LoadingModList.get().getMods().stream().map(ModInfo::getModId).toList();
        String relativeName = mixinClassName.substring(getClass().getPackageName().length() + 1);
        String packageName = relativeName.substring(0, relativeName.lastIndexOf('.'));
        for (String segment : packageName.split("\\.")) {
            if ("client".equals(segment) || "server".equals(segment) || "common".equals(segment)) {
                return true;
            }
            if (!modIds.contains(segment)) return false;
        }
        return true;
    }

    @Override
    public void acceptTargets(Set<String> myTargets, Set<String> otherTargets) {

    }

    @Override
    public List<String> getMixins() {
        return List.of();
    }

    @Override
    public void preApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) {

    }

    @Override
    public void postApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) {

    }
}
