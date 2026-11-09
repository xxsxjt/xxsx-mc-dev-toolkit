package io.zershyan.examplemod.datagen.lang;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.util.LazyComponent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;

import java.util.ArrayList;
import java.util.List;

public class ExampleModKeyLang extends ExampleModLang {
    private static final List<FinalEntry<String>> TranslatableLang = new ArrayList<>();
    private static final String ModId = ExampleMod.MODID;
    private static final String ModName = ExampleMod.class.getSimpleName();

    public static final MutableComponent CreativeTab = entry("item_group." + ModId + "." + ModId, ModName, "示例");
    public static final MutableComponent Resource = entry(ModId + ".resources", "Resources for " + ModName, ModName + "资源");

    private static final String CommandPrefix = "command." + ModId + ".";
    private static final String ErrorPrefix = "error." + ModId + ".";
    private static final String TooltipPrefix = "tooltip." + ModId + ".";
    private static final String DescriptionPrefix = "description." + ModId + ".";
    private static final String MessagePrefix = "message." + ModId + ".";

    // 按键
    public static final String KeyCategory = entryString(getKeyDesc("category"), ModName, ModName);
    public static final String KeyAction = entryString(getKeyDesc("action"), "Example Action", "示例动作");

    // 命令
    public static final LazyComponent CommandValueSet = entryLazy(CommandPrefix + "value_set",
            "Value set to %s",
            "数值已设为 %s");

    // 物品提示
    public static final MutableComponent ItemExampleDesc = entry(TooltipPrefix + "example_item.desc",
            "An example item.",
            "示例物品");

    // 错误
    public static final MutableComponent ErrorAttachment = entry(ErrorPrefix + "attachment",
            "Attachment Error.",
            "附件数据异常");

    private static String entryString(String key, String enUs, String zhCn) {
        TranslatableLang.add(new FinalEntry<>(key, enUs, zhCn));
        return key;
    }

    private static MutableComponent entry(String key, String enUs, String zhCn) {
        return Component.translatable(entryString(key, enUs, zhCn));
    }

    private static LazyComponent entryLazy(String key, String enUs, String zhCn) {
        return new LazyComponent(entryString(key, enUs, zhCn));
    }

    @Override
    public List<Entry> init(List<Entry> entries) {
        entries.addAll(TranslatableLang);
        return entries;
    }
}
