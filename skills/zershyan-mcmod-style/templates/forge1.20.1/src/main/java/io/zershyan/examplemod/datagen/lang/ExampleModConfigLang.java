package io.zershyan.examplemod.datagen.lang;

import io.zershyan.examplemod.datagen.util.ConfigLangEntry;

import java.util.ArrayList;
import java.util.List;

public class ExampleModConfigLang extends ExampleModLang {
    private static final List<FinalEntry<String>> TranslatableLang = new ArrayList<>();

    public static final ConfigLangEntry EnableFeature = entry("enable_feature", "Enable Feature", "启用示例功能");
    public static final ConfigLangEntry ShowOverlay = entry("show_overlay", "Show Overlay", "显示示例叠层");
    public static final ConfigLangEntry MaxValue = entry("max_value", "Max Value", "数值上限");

    private static ConfigLangEntry entry(String name, String enUs, String zhCn) {
        ConfigLangEntry langEntry = new ConfigLangEntry(name);
        TranslatableLang.add(new FinalEntry<>(langEntry.key(), enUs, zhCn));
        return langEntry;
    }

    @Override
    protected List<Entry> init(List<Entry> entries) {
        entries.addAll(TranslatableLang);
        return entries;
    }
}
